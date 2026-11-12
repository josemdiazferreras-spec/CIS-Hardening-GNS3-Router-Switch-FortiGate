#!/usr/bin/env python3
"""Una sola ejecucion para auditoria/hardening de R1 + SW + FortiGate.

Modo auditar: nunca envia configuracion.
Modo aplicar: solicita confirmacion y realiza auditoria antes y despues.
Seleccion reducida de controles de laboratorio, NO certificacion CIS.
No guarda credenciales en archivos ni publica configuraciones completas.

Uso:
    python cis_tres_dispositivos.py auditar
    python cis_tres_dispositivos.py aplicar
"""
import argparse
from datetime import datetime
from getpass import getpass
import json
from pathlib import Path
import sys

from netmiko import ConnectHandler
import cis_cisco_base as cisco
import fortigate_cis_v2 as forti

CARPETA = Path(__file__).resolve().parent / 'informes'


def mostrar_cisco(controles):
    for item in controles.values():
        print('  [{}] {}'.format('CUMPLE' if item['cumple'] else 'NO CUMPLE', item['detalle']))
    print('  Puntuacion: {}/{}'.format(sum(i['cumple'] for i in controles.values()), len(controles)))


def revisar_cisco(nombre, ip, modo):
    print('\n===== {} ({}) ====='.format(nombre, ip))
    usuario = input('Usuario SSH [{}]: '.format('auditor')).strip() or 'auditor'
    clave = getpass('Contrasena SSH de {}: '.format(nombre))
    resultado = {'ip': ip, 'tipo': 'Cisco IOS', 'guardado_en_nvram': None}
    try:
        with ConnectHandler(device_type='cisco_ios', host=ip, username=usuario,
                            password=clave, conn_timeout=30, auth_timeout=30) as conexion:
            antes = cisco.read_state(conexion)
            resultado['antes'] = antes
            mostrar_cisco(antes)
            if modo == 'aplicar':
                resultado['reglas_aplicadas'] = cisco.apply_selected(conexion, antes)
                despues = cisco.read_state(conexion)
                resultado['despues'] = despues
                print('  --- DESPUES ---')
                mostrar_cisco(despues)
                resultado['guardado_en_nvram'] = False
                print('  AVISO: cambios IOS en RAM. Guardar manualmente con write memory tras comprobarlos.')
    except Exception as exc:
        resultado['error'] = '{}: {}'.format(type(exc).__name__, exc)
        print('  ERROR {}: {}'.format(nombre, resultado['error']))
    return resultado


def revisar_forti(modo):
    print('\n===== FORTIGATE (10.6.94.3) =====')
    usuario = input('Usuario FortiGate [admin]: ').strip() or 'admin'
    clave = getpass('Contrasena SSH de FortiGate: ')
    resultado = {'ip': '10.6.94.3', 'tipo': 'FortiOS 7.0.9',
                 'guardado_automatico': True}
    try:
        with forti.conectar(usuario, clave) as conexion:
            globales, acceso = forti.obtener_estado(conexion)
            antes = forti.evaluar(globales, acceso)
            resultado['antes'] = antes
            forti.mostrar(antes, '--- AUDITORIA INICIAL ---')
            if modo == 'aplicar':
                try:
                    resultado['acciones'] = forti.aplicar(conexion, globales, acceso,
                                                        antes, autorizado=True)
                except Exception as exc:
                    resultado['incidencia_aplicacion'] = '{}: {}'.format(type(exc).__name__, exc)
                    print('  AVISO: la sesion pudo interrumpirse durante los cambios. Se intentara reconectar.')
        if modo == 'aplicar':
            # Comprobar desde una SESION NUEVA, incluso si el cifrado cambió.
            with forti.conectar(usuario, clave) as conexion:
                globales, acceso = forti.obtener_estado(conexion)
            despues = forti.evaluar(globales, acceso)
            resultado['despues'] = despues
            forti.mostrar(despues, '--- AUDITORIA POSTERIOR ---')
    except Exception as exc:
        resultado['error'] = '{}: {}'.format(type(exc).__name__, exc)
        print('  ERROR FortiGate: {}'.format(resultado['error']))
        print('  Si cambian los cifrados TLS o la sesion SSH, comprobar acceso en la consola de GNS3.')
    return resultado


def resumen(dispositivos, modo):
    print('\n===== RESUMEN DE LOS TRES EQUIPOS =====')
    total = 0
    aprobados = 0
    for nombre, datos in dispositivos.items():
        controles = datos.get('despues') if modo == 'aplicar' else datos.get('antes')
        if not controles:
            print('  {}: SIN RESULTADO (revisar error)'.format(nombre))
            continue
        if nombre == 'FW1':
            ok = sum(controles.values())
        else:
            ok = sum(x['cumple'] for x in controles.values())
        print('  {}: {}/{}'.format(nombre, ok, len(controles)))
        total += len(controles)
        aprobados += ok
    print('  TOTAL COMPROBADO: {}/{}'.format(aprobados, total))
    if total < 21:
        print('  AVISO: faltan resultados de uno o mas dispositivos.')
    return aprobados, total


def principal():
    parser = argparse.ArgumentParser(description='GNS3: R1, SW y FortiGate; 2 modos')
    parser.add_argument('modo', choices=['auditar', 'aplicar'])
    args = parser.parse_args()
    print('===== CIS HARDENING ORIENTATIVO - TRES DISPOSITIVOS =====')
    print('Modo: {} | 7 controles por equipo; no es certificacion CIS.'.format(args.modo))
    print('R1=10.6.94.1, SW=10.6.94.2, FortiGate=10.6.94.3')
    print('No se guardan claves ni configuraciones completas en los informes.')
    if args.modo == 'aplicar':
        print('\nADVERTENCIA: modifica configuraciones reales de los tres equipos GNS3.')
        print('Cisco: cambios activos no persistentes hasta write memory.')
        print('FortiGate: guarda cambios automaticamente; algunos ajustes criptograficos pueden afectar sesiones; verificar acceso.')
        if input('Para autorizar los cambios escriba APLICAR: ').strip() != 'APLICAR':
            print('Cancelado; no se ha modificado ningun equipo.')
            return 1
    CARPETA.mkdir(exist_ok=True, parents=True)
    dispositivos = {}
    for nombre, ip in cisco.DEVICES.items():
        dispositivos[nombre] = revisar_cisco(nombre, ip, args.modo)
    dispositivos['FW1'] = revisar_forti(args.modo)
    aprobados, total = resumen(dispositivos, args.modo)
    fecha = datetime.now().astimezone()
    informe = {
        'fecha': fecha.isoformat(timespec='seconds'),
        'modo': args.modo,
        'alcance': '21 controles seleccionados (7 por dispositivo). No constituye certificacion CIS.',
        'nota': 'Conservar informes antes/despues; no publicar contrasenas o running-config sin sanitizar.',
        'dispositivos': dispositivos,
        'resultado': {'aprobados': aprobados, 'evaluados': total, 'esperados': 21}
    }
    destino = CARPETA / 'tres_dispositivos_{}_{:%Y%m%d_%H%M%S}.json'.format(args.modo, fecha)
    destino.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\nInforme combinado guardado: {}'.format(destino))
    return 1 if total < 21 or any('error' in d or 'incidencia_aplicacion' in d for d in dispositivos.values()) else 0


if __name__ == '__main__':
    sys.exit(principal())
