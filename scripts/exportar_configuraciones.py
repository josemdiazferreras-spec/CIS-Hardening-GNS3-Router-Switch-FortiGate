#!/usr/bin/env python3
"""Recupera running-configs desde GNS3 sin aplicar cambios; versión pública requiere revisión.
No publica automáticamente en GitHub.
"""
from pathlib import Path
from getpass import getpass
import re
from netmiko import ConnectHandler

DEVICES = {'R1': '10.6.94.1', 'SW': '10.6.94.2'}
OUT = Path(__file__).resolve().parent.parent / 'configs'

# Mantiene solo comentario indicativo, no el valor secreto.
SECRET_LINE = re.compile(
    r'(?i)^\s*(?:username\s+\S+\s+.*\b(?:secret|password)\b|'
    r'enable\s+(?:secret|password)|password\s+|secret\s+|'
    r'snmp-server\s+(?:community|user|host)|'
    r'(?:radius|tacacs)-server\s+key|'
    r'key-string|crypto\s+isakmp\s+key|'
    r'ntp\s+authentication-key|'
    r'ip\s+ospf\s+authentication-key)'
)

def sanitize(data: str) -> str:
    lines = ['! PUBLICADO SOLO TRAS REVISION MANUAL DE SECRETOS']
    skipping_banner = None
    for line in data.splitlines():
        stripped = line.strip()
        if skipping_banner:
            if skipping_banner in line:
                skipping_banner = None
            continue
        m = re.match(r'^banner\s+\S+\s+(\S+)', stripped)
        if m:
            skipping_banner = m.group(1)
            lines.append('! [BANNER OMITIDO]')
            continue
        if SECRET_LINE.search(line) or re.search(r'(?i)\b(?:private-key|pre-shared-key|key 7)\b', line):
            lines.append('! [LINEA SENSIBLE OMITIDA]')
            continue
        lines.append(line)
    return '\n'.join(lines) + '\n'

def main():
    OUT.mkdir(exist_ok=True)
    for name, ip in DEVICES.items():
        print(f'Exportando {name}: {ip}')
        user = input('Usuario SSH [auditor]: ').strip() or 'auditor'
        password = getpass('Contraseña SSH: ')
        with ConnectHandler(device_type='cisco_ios', host=ip,
                            username=user, password=password,
                            conn_timeout=30) as connection:
            config = connection.send_command('show running-config', read_timeout=90)
        filename = OUT / f'{name}_running-config_final_sanitizado.txt'
        filename.write_text(sanitize(config), encoding='utf-8')
        print(f'Archivo creado: {filename} (REVISAR antes de compartir)')

if __name__ == '__main__':
    main()
