# Guía para reproducir el laboratorio en una topología propia

## Dependencias

- GNS3 con dispositivos Cisco autorizados y Kali Linux.
- R1 `10.6.94.1`, SW `10.6.94.2`, Kali `10.6.94.10` con conectividad comprobada.
- SSHv2 habilitado en ambos Cisco y credenciales administrativas locales válidas (no publicar contraseñas).
- Python 3.13 en un `venv`, Netmiko 4.8.0 y Paramiko 3.5.1 para esta plataforma antigua.

## 1. Preparar Kali

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
```

## 2. Auditar sin hacer cambios

```bash
python scripts/cis_hardening.py auditar
```

Se generará un JSON en `scripts/informes/` porque el script crea los informes al lado de sí mismo. Los reportes de las ejecuciones anteriores del estudiante se encuentran originalmente bajo `~/cis-hardening/CIS-Hardening-GNS3/informes/` y se recopilarán en `docs/informes/` para publicación.

## 3. Aplicar hardening controlado

```bash
python scripts/cis_hardening.py aplicar
```

Solo en un entorno propio autorizado. El programa requiere confirmar con la palabra `APLICAR`; modifica HTTP/HTTPS administrativos y tiempos de espera únicamente cuando no cumplen, ejecuta una segunda revisión y genera un JSON. **No guarda en NVRAM automáticamente.**

## 4. Verificar conectividad y conservar configuración

```bash
ping -c 5 10.6.94.1
ping -c 5 10.6.94.2
```

En la consola de cada Cisco, tras comprobar los resultados:

```text
copy running-config startup-config
```

## 5. Exportar configuraciones para documentación

Desde Kali en el repositorio:

```bash
python scripts/exportar_configuraciones.py
```

Este script utiliza `show running-config`, no modifica los equipos y genera archivos sanitizados dentro de `configs/`. **Verificar manualmente** todo el contenido antes de hacerlo público: el filtro automático no garantiza eliminar todos los secretos.
