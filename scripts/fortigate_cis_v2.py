#!/usr/bin/env python3
"""FortiGate GNS3: auditoria orientativa y hardening aprobado (FortiOS 7.0.9).

  python fortigate_cis_v2.py auditar   # solo lectura (por defecto)
  python fortigate_cis_v2.py aplicar   # requiere confirmacion APLICAR

Conserva los controles de la auditoria inicial de 7 puntos. No equivale a
certificacion completa CIS. No almacena contrasenas ni configuraciones sensibles.
"""

import argparse
import json
import re
from datetime import datetime
from getpass import getpass
from pathlib import Path

from netmiko import ConnectHandler

IP = "10.6.94.3"
CARPETA = Path(__file__).resolve().parent / "informes"


def parametros_globales(salida):
    valores = {}
    for linea in salida.splitlines():
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            valores[clave.strip()] = valor.strip()
    return valores


def lista_acceso(salida):
    for linea in salida.splitlines():
        linea = linea.strip()
        if linea.startswith("set allowaccess "):
            return linea.split()[2:]
    return None


def en_rango(valor, minimo, maximo):
    try:
        return minimo <= int(valor) <= maximo
    except (TypeError, ValueError):
        return False


def obtener_estado(conexion):
    globales = conexion.send_command("get system global", read_timeout=60)
    interfaz = conexion.send_command("show system interface port1", read_timeout=30)
    return parametros_globales(globales), lista_acceso(interfaz)


def evaluar(parametros, acceso):
    return {
        "SSH version 1 deshabilitado": parametros.get("admin-ssh-v1") == "disable",
        "Telnet administrativo global deshabilitado": parametros.get("admin-telnet") == "disable",
        "Cifrados TLS estaticos deshabilitados": parametros.get("ssl-static-key-ciphers") == "disable",
        "Auditoria de comandos CLI habilitada": parametros.get("cli-audit-log") == "enable",
        "HTTP administrativo deshabilitado en port1": acceso is not None and "http" not in acceso,
        "Tiempo de inactividad administrativo entre 1 y 10 minutos": en_rango(parametros.get("admintimeout"), 1, 10),
        "Bloqueo tras 1 a 3 intentos fallidos": en_rango(parametros.get("admin-lockout-threshold"), 1, 3),
    }


def mostrar(controles, titulo):
    print("\n" + titulo)
    for nombre, ok in controles.items():
        print(f"[{'CUMPLE' if ok else 'NO CUMPLE'}] {nombre}")
    print(f"TOTAL: {sum(controles.values())}/{len(controles)}")


def guardar(controles, modo, observaciones=None):
    CARPETA.mkdir(parents=True, exist_ok=True)
    fecha = datetime.now().astimezone()
    archivo = CARPETA / f"fortigate_{modo}_{fecha:%Y%m%d_%H%M%S}.json"
    informe = {
        "dispositivo": "FortiGate", "ip": IP, "modo": modo,
        "fecha": fecha.isoformat(timespec="seconds"),
        "alcance": "7 controles de laboratorio orientados a CIS; no certificacion oficial",
        "controles": controles,
        "aprobados": sum(controles.values()), "total": len(controles),
        "observaciones": observaciones or [],
    }
    archivo.write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Informe guardado: {archivo}")


def comando(conexion, instruccion):
    salida = conexion.send_command_timing(instruccion, read_timeout=35)
    if re.search(r"(?i)(command parse error|unknown action|error code|return code\s*-\d+|invalid syntax|object set operator error)", salida):
        raise RuntimeError(f"FortiOS rechazo '{instruccion}': {salida.strip()}")
    return salida


def aplicar(conexion, parametros, acceso, controles, autorizado=False):
    if acceso is None or "ssh" not in acceso:
        raise RuntimeError("No se puede verificar SSH en port1. Se cancela para prevenir perdida de acceso.")
    fallos = [nombre for nombre, ok in controles.items() if not ok]
    if not fallos:
        print("Los 7 controles ya cumplen; no hay cambios que aplicar.")
        return []
    print("\nCAMBIOS PROPUESTOS:")
    for nombre in fallos:
        print(" - " + nombre)
    print("Se conservaran IP, puertos SSH/HTTPS, rutas y politicas de firewall.")
    print("ADVERTENCIA: ssl-static-key-ciphers puede reiniciar/interrumpir la sesion SSH.")
    if not autorizado and input("Para autorizar, escriba APLICAR: ").strip() != "APLICAR":
        print("Cancelado. No se aplicaron cambios.")
        return ["Cancelado por el operador"]

    observaciones = []
    globales = []
    if parametros.get("admin-telnet") != "disable":
        globales.append("set admin-telnet disable")
    if parametros.get("cli-audit-log") != "enable":
        globales.append("set cli-audit-log enable")

    if globales:
        comando(conexion, "config system global")
        try:
            for c in globales:
                comando(conexion, c)
                observaciones.append("Solicitado: " + c)
        finally:
            comando(conexion, "end")

    if "http" in acceso:
        permitido = [x for x in acceso if x != "http"]
        if "ssh" not in permitido:
            raise RuntimeError("Configuracion sin SSH: operacion detenida")
        comando(conexion, "config system interface")
        try:
            comando(conexion, 'edit "port1"')
            comando(conexion, "set allowaccess " + " ".join(permitido))
            observaciones.append("Solicitado: retirar HTTP de port1 (conservar SSH y otros accesos)")
            comando(conexion, "next")
        finally:
            comando(conexion, "end")

    # Ejecutar al final: puede modificar los algoritmos SSH disponibles.
    if parametros.get("ssl-static-key-ciphers") != "disable":
        comando(conexion, "config system global")
        try:
            comando(conexion, "set ssl-static-key-ciphers disable")
            observaciones.append("Solicitado: set ssl-static-key-ciphers disable")
        finally:
            try:
                comando(conexion, "end")
            except Exception as exc:
                observaciones.append("Sesion SSH interrumpida al activar ssl-static-key-ciphers: " + type(exc).__name__)
                print("La sesion pudo cerrarse al cambiar cifrados. Verificaremos reconectando.")
    return observaciones


def conectar(usuario, clave):
    return ConnectHandler(
        device_type="fortinet", host=IP, username=usuario, password=clave,
        conn_timeout=30, auth_timeout=30,
    )


def principal():
    p = argparse.ArgumentParser(description="Auditoria y hardening FortiGate de laboratorio")
    p.add_argument("modo", nargs="?", choices=["auditar", "aplicar"], default="auditar")
    args = p.parse_args()
    print("=== FORTIGATE |", args.modo.upper(), "===")
    usuario = input("Usuario SSH [admin]: ").strip() or "admin"
    clave = getpass("Contrasena de FortiGate: ")
    try:
        with conectar(usuario, clave) as conexion:
            parametros, acceso = obtener_estado(conexion)
            antes = evaluar(parametros, acceso)
            mostrar(antes, "--- AUDITORIA INICIAL ---")
            if args.modo == "auditar":
                guardar(antes, "auditar")
                return 0
            # Conservar el antes aunque se interrumpa la aplicacion.
            guardar(antes, "antes")
            observaciones = aplicar(conexion, parametros, acceso, antes)
    except Exception as exc:
        print(f"ERROR antes/durante la aplicacion: {type(exc).__name__}: {exc}")
        print("Revise la consola de GNS3; no presuponga que se aplicaron todos los cambios.")
        return 1
    if observaciones == ["Cancelado por el operador"]:
        return 0
    try:
        with conectar(usuario, clave) as conexion:
            parametros, acceso = obtener_estado(conexion)
        despues = evaluar(parametros, acceso)
        mostrar(despues, "--- AUDITORIA POSTERIOR ---")
        guardar(despues, "despues", observaciones)
        if not all(despues.values()):
            print("ATENCION: no todos los controles cumplen; revisar antes de dar la practica por finalizada.")
            return 2
        print("Se verificaron 7/7 controles de esta seleccion de laboratorio.")
        return 0
    except Exception as exc:
        print(f"No se pudo auditar despues: {type(exc).__name__}: {exc}")
        print("Revise la consola FortiGate y vuelva a ejecutar 'auditar'.")
        return 1


if __name__ == "__main__":
    raise SystemExit(principal())
