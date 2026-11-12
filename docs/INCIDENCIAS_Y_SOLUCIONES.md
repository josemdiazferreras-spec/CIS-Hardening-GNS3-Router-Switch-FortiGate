# Incidencias identificadas y soluciones

| Incidencia | Diagnóstico | Solución verificada |
|---|---|---|
| Kali sin IP IPv4 | Interfaz `eth0` solo con IPv6 local | IP temporal `10.6.94.10/24`, gateway `10.6.94.1` |
| Kali sin Internet | Faltaba NAT/PAT entre LAN y WAN de R1 | Configuración `ip nat inside/outside` y overload ACL 20; ping externo 5/5 |
| Kali sin DNS | Faltaba `/etc/resolv.conf` | DNS `8.8.8.8`, resolución `pypi.org` validada |
| Cliente SSH moderno rechazaba al router antiguo | Incompatibilidad de KEX, hostkey y cifrado CBC | Opciones temporales por sesión para pruebas de laboratorio; no una mejora de seguridad |
| Netmiko fallaba en negociación KEX | Paramiko moderno incompatible con el IOS de R1 | Entorno virtual con Netmiko 4.8.0 y Paramiko 3.5.1; conexiones de prueba exitosas |
| Auditoría inicial rechazó ambos logins | Se introdujo `123` como nombre de usuario | Utilizar usuario `auditor` y contraseña válida |
| Python no se podía pegar en Nano por TightVNC | Portapapeles no transfería contenido | Se preparó archivo en Windows y descargó desde GitHub con `git clone` |

Las soluciones reflejan hechos visibles en capturas; se incluyen para explicar el proceso, no como recomendaciones universales de hardening.
