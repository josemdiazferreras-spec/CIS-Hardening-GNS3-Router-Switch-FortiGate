#!/usr/bin/env python3
"""Auditoría y hardening básico para laboratorios Cisco IOS con Netmiko.

Controles SELECCIONADOS relacionados con buenas prácticas CIS. No es un
escáner completo CIS ni declara cumplimiento oficial. Usar únicamente en
los propios equipos GNS3.
"""
import argparse
from datetime import datetime
from getpass import getpass
import json
from pathlib import Path
import re
import sys

from netmiko import ConnectHandler

DEVICES = {"R1": "10.6.94.1", "SW": "10.6.94.2"}
REPORT_DIR = Path(__file__).resolve().parent / "informes"

# Cuatro cambios conservadores: no altera SSH, usuarios, claves ni interfaces.
REMEDIATIONS = {
    "http_off": ("no ip http server",),
    "https_off": ("no ip http secure-server",),
    "console_timeout": ("line con 0", "exec-timeout 5 0"),
    "vty_timeout": ("line vty 0 4", "exec-timeout 5 0"),
}


def section(config: str, prefix: str) -> list[str]:
    """Extrae una sección de primer nivel de show running-config."""
    lines = config.splitlines()
    found = False
    result = []
    for line in lines:
        if not found:
            if line.strip() == prefix:
                found = True
            continue
        if line.strip() == "!":
            break
        if line and not line[0].isspace():
            break
        if line.strip():
            result.append(line.strip())
    return result


def audit(config: str, ssh_output: str) -> dict:
    lines = [line.strip() for line in config.splitlines()]
    console = section(config, "line con 0")
    vty = section(config, "line vty 0 4")

    def timeout_is_safe(values):
        for value in values:
            match = re.fullmatch(r"exec-timeout\s+(\d+)\s+(\d+)", value)
            if match:
                minutes, seconds = map(int, match.groups())
                return 0 < (minutes * 60 + seconds) <= 600
        return False  # Ausencia: sin evidencia explícita de cumplimiento.

    checks = {
        "http_off": "no ip http server" in lines and "ip http server" not in lines,
        "https_off": "no ip http secure-server" in lines and "ip http secure-server" not in lines,
        "console_timeout": timeout_is_safe(console),
        "vty_timeout": timeout_is_safe(vty),
        "ssh_v2": "SSH Enabled - version 2.0" in ssh_output,
        "vty_ssh_only": "transport input ssh" in vty,
        "vty_local_login": "login local" in vty,
    }
    return {
        key: {"cumple": value, "detalle": CONTROL_LABELS[key]}
        for key, value in checks.items()
    }


CONTROL_LABELS = {
    "http_off": "Servidor HTTP administrativo deshabilitado",
    "https_off": "Servidor HTTPS administrativo deshabilitado (no requerido en este laboratorio)",
    "console_timeout": "Consola con tiempo de inactividad explícito (1-10 minutos)",
    "vty_timeout": "VTY con tiempo de inactividad explícito (1-10 minutos)",
    "ssh_v2": "SSH versión 2 habilitado",
    "vty_ssh_only": "Acceso remoto restringido a SSH",
    "vty_local_login": "VTY autenticada con usuarios locales",
}


def read_state(connection):
    config = connection.send_command("show running-config", read_timeout=90)
    ssh = connection.send_command("show ip ssh", read_timeout=35)
    return audit(config, ssh)


def print_checks(checks):
    for key, info in checks.items():
        state = "CUMPLE" if info["cumple"] else "NO CUMPLE"
        print(f"  [{state}] {info['detalle']}")


def apply_selected(connection, before):
    """Solo aplica controles no conformes aprobados para este laboratorio."""
    applied = []
    for control in REMEDIATIONS:
        if before[control]["cumple"]:
            continue
        commands = list(REMEDIATIONS[control])
        print(f"  Aplicando: {CONTROL_LABELS[control]}")
        output = connection.send_config_set(commands, read_timeout=60)
        if re.search(r"% (Invalid|Error|Incomplete|Ambiguous)", output, flags=re.I):
            raise RuntimeError(f"IOS rechazó una orden de {control}: {output[-400:]}")
        applied.append(control)
    return applied


def main():
    parser = argparse.ArgumentParser(
        description="Auditoría CIS orientativa o hardening controlado de R1 y SW"
    )
    parser.add_argument("modo", choices=["auditar", "aplicar"],
                        help="auditar: solo lectura; aplicar: cambios aprobados + auditoría posterior")
    args = parser.parse_args()

    print(f"\n=== CIS HARDENING (laboratorio) | {args.modo.upper()} ===")
    print("Dispositivos: R1 (10.6.94.1), SW (10.6.94.2)")
    print("Alcance: 7 comprobaciones seleccionadas; NO certifica cumplimiento CIS.")
    if args.modo == "aplicar":
        print("Cambios posibles: deshabilitar servidores HTTP/HTTPS y configurar")
        print("tiempos de espera en consola/VTY. No modifica usuarios, SSH ni interfaces.")
        response = input("¿Autoriza aplicar esos cambios a AMBOS equipos? Escriba APLICAR: ")
        if response != "APLICAR":
            print("Cancelado. No se realizaron cambios.")
            return 1

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "modo": args.modo,
        "alcance": "Controles seleccionados de hardening Cisco IOS; no auditoría CIS certificada",
        "nota": "No subir running-configs con hashes o credenciales a repositorios públicos.",
        "dispositivos": {},
    }

    for name, ip in DEVICES.items():
        print(f"\n--- {name} ({ip}) ---")
        username = input(f"Usuario SSH de {name} [auditor]: ").strip() or "auditor"
        password = getpass(f"Contraseña SSH de {name}: ")
        params = {
            "device_type": "cisco_ios", "host": ip,
            "username": username, "password": password,
            "conn_timeout": 30, "auth_timeout": 30,
        }
        result = {"ip": ip}
        try:
            with ConnectHandler(**params) as conn:
                before = read_state(conn)
                result["antes"] = before
                print_checks(before)
                if args.modo == "aplicar":
                    result["reglas_aplicadas"] = apply_selected(conn, before)
                    after = read_state(conn)
                    result["despues"] = after
                    print("  Resultado posterior:")
                    print_checks(after)
                    # No se hace 'write memory' automáticamente, para poder
                    # probar y revisar los cambios antes de hacerlos persistentes.
                    result["guardado_en_nvram"] = False
                    print("  IMPORTANTE: cambios activos; no guardados en NVRAM.")
        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"
            print(f"  ERROR en {name}: {type(exc).__name__}: {exc}")
        report["dispositivos"][name] = result

    output_path = REPORT_DIR / f"{args.modo}_{timestamp}.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nInforme guardado: {output_path}")
    print("Modo auditar: no aplica cambios. Modo aplicar: cambios activos, no persistentes.")
    return 1 if any("error" in result for result in report["dispositivos"].values()) else 0


if __name__ == "__main__":
    sys.exit(main())
