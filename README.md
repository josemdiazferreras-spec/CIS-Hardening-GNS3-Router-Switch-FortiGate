# Hardening CIS orientativo en GNS3 — Router + Switch + FortiGate

## 🎥 Video demostrativo de los TRES dispositivos

**Video histórico de la etapa Cisco R1 + SW (no incluye FortiGate):** https://youtu.be/4RRuTz3-xdg. Se conserva como evidencia anterior, pero **no reemplaza el nuevo video**.

**Estudiante:** José Miguel Díaz Ferreras  
**Matrícula:** `2025-0693`  
**Herramientas:** GNS3 · Cisco IOS 15.2 · FortiOS 7.0.9 · Kali Linux · Python · Netmiko 4.8.0 · Paramiko 3.5.1.

> Laboratorio académico con controles **seleccionados** de hardening inspirados en criterios CIS. Los porcentajes corresponden a **esta matriz de controles**, no a una certificación CIS Benchmark general.


![Topología real GNS3, router, switch, firewall, Kali y PC1](images/evidencias/fortigate_01_topologia_gns3_router_switch_fortigate_pc_kali.png)

## 1. Propósito y alcance

**Documentar una sola infraestructura completa: R1 Cisco, SW Cisco, FortiGate, Kali y PC1**, con segmentación de redes, políticas de filtrado, pruebas de tráfico permitido y rechazado, y auditoría/hardening automatizados. Se preservan sin alteraciones todos los scripts, informes y evidencias de las auditorías anteriores de R1 y SW.

## 2. Arquitectura

| Equipo / interfaz | IP | Propósito |
|---|---|---|
| R1 Cisco Fa0/0 | 10.6.94.1/24 | Puerta de enlace principal |
| SW Cisco VLAN1 | 10.6.94.2/24 | Gestión del switch |
| Kali Auditor eth0 | 10.6.94.10/24 | Auditoría y verificación |
| FortiGate port1 | 10.6.94.3/24 | Enlace al SW Gi0/2 |
| FortiGate port2 | 10.6.95.1/24 | Red protegida |
| PC1 VPCS | 10.6.95.10/24 | Pruebas de control de acceso |
| R1 Gi1/0 (WAN) | DHCP vía NAT1 | Salida externa |


## 3. Router R1 y Switch SW — auditoría y hardening

Se configuró el acceso SSHv2 para R1 y SW, con autenticación local, VTY restringidas a SSH, desactivación de servicios HTTP/HTTPS no necesarios en este laboratorio y tiempos `exec-timeout 5 0` para sesiones abandonadas. Se utilizó Kali con Netmiko para comprobar cada control y aplicar cambios previa confirmación. El equipo auditor también probó la conectividad de R1 y SW tras el hardening.

| Dispositivo | Auditoría inicial | Auditoría final |
|---|---:|---:|
| Router R1 | **5/7** | **7/7** |
| Switch SW | **3/7** | **7/7** |
| **Total Cisco** | **8/14** | **14/14** |

![Auditoría original Cisco 8 de 14](images/evidencias/cisco_05_auditoria_inicial_8_de_14.png)

![Auditoría posterior Cisco 14 de 14](images/evidencias/cisco_09_auditoria_final_14_de_14.png)

**Pruebas preservadas sin borrar:** capturas de Cisco (prefijo `cisco_`) en [`images/evidencias/`](images/evidencias/), acceso Netmiko router y switch, evidencia de autorización, aplicación automática a R1/SW y ping final Kali→R1, Kali→SW de 5/5 respuestas. Permanecen igualmente los JSON auténticos en [`docs/informes/`](docs/informes/), el script original [`scripts/cis_hardening.py`](scripts/cis_hardening.py) y las copias saneadas de configuración en [`configs/`](configs/).

Material de archivo Cisco, conservado sin cambios: [Word original](docs/Documento_Tecnico_CIS_Hardening_Jose_Miguel_Diaz_Ferreras.docx) · [PDF original](docs/Documento_Tecnico_CIS_Hardening_Jose_Miguel_Diaz_Ferreras.pdf) · [documento técnico original](docs/DOCUMENTO_TECNICO.md) · [README original](README_CISCO_SW_ORIGINAL.md).

## 4. Firewall FortiGate — configuración y pruebas de filtrado

FortiOS 7.0.9 se conecta al switch mediante port1 y protege la subred de PC1 a través de port2. Se configuraron dos subredes y una política explícita `PC1_A_KALI_SOLO_PING` que autoriza únicamente servicio `PING` desde PC1 (`10.6.95.10`) a Kali (`10.6.94.10`) con NAT y logging. Los otros flujos sin política se rechazan por la regla implícita.

**Pruebas finales medidas:** PC1→Kali **5/5**, PC1→SW **0/5**. La consola de FortiGate confirmó cinco veces **`Denied by forward policy check (policy 0)`** para el tráfico PC1→SW; de este modo el bloqueo no se infiere solo por la pérdida de paquetes.

![SSH Kali hacia FortiGate](images/evidencias/fortigate_03_ssh_kali_fortigate_exitoso.png)

![Auditoría inicial FortiGate 3 de 7](images/evidencias/fortigate_04_auditoria_inicial_fortigate_3_7.png)

Documentación detallada: [**AMPLIACIÓN FORTIGATE COMPLETA**](docs/AMPLIACION_FORTIGATE.md) · [**PRUEBAS DE TRÁFICO**](docs/PRUEBAS_FORTIGATE_Y_VALIDACION.md) · [extractos FortiGate saneados](configs/FortiGate_fragmentos_verificados_sin_credenciales.txt).

## 5. Script automatizado de los tres dispositivos

El código Python consulta Cisco IOS y FortiOS a través de SSH. **`auditar` no modifica** los dispositivos; **`aplicar` requiere confirmación `APLICAR`**, solicita las credenciales sin almacenarlas y comprueba el estado posterior. Al ejecutarse, guarda JSON en `scripts/informes/`.

| Archivo | Función |
|---|---|
| [`scripts/cis_hardening.py`](scripts/cis_hardening.py) | **Script Cisco original intacto**: 2 dispositivos, 2 modos |
| [`scripts/cis_tres_dispositivos.py`](scripts/cis_tres_dispositivos.py) | **Programa integrado nuevo**: R1 + SW + FortiGate |
| [`scripts/cis_cisco_base.py`](scripts/cis_cisco_base.py) | Funciones de auditoría/aplicación Cisco para el programa integrado |
| [`scripts/fortigate_cis_v2.py`](scripts/fortigate_cis_v2.py) | Funciones auditables de FortiGate, con control TLS alternativo |
| [`scripts/requirements.txt`](scripts/requirements.txt) | Dependencias del ambiente de Python (revisar versiones compatibles) |

Desde la raíz del repositorio, en un entorno con acceso y permiso a los equipos:

```bash
python scripts/cis_tres_dispositivos.py auditar
```

El modo de aplicación (`python scripts/cis_tres_dispositivos.py aplicar`) **cambia configuraciones reales** y solo debe ejecutarse sobre el laboratorio propio, con copia de seguridad y autorización. **No hace falta volver a aplicar** en dispositivos ya endurecidos; para el video puede mostrarse el informe histórico y ejecutar solo lectura.

## 6. Resultados reales y comparación temporal

![Evolución del laboratorio](images/evidencias/diagrama_flujo_tres_dispositivos.png)

| Momento | Cisco R1 | Cisco SW | FortiGate | Resultado |
|---|---:|---:|---:|---:|
| Auditoría Cisco (registro inicial) | 5/7 | 3/7 | — | **8/14** |
| Auditoría Cisco (registro posterior) | 7/7 | 7/7 | — | **14/14** |
| Auditoría conjunta, antes del hardening FortiGate | 7/7 | 7/7 | 3/7 | **17/21** |
| Tras aplicar automáticamente los cambios al firewall | 7/7 | 7/7 | 6/7 | **20/21** |
| Auditoría final con **matriz revisada** | 7/7 | 7/7 | 7/7 | **21/21** |

![Auditoría final 21 de 21](images/evidencias/fortigate_07_auditoria_final_tres_dispositivos_21_21.png)

### Incidencia criptográfica: transparencia en el informe

La VM FortiGate mostró `strong-crypto: disable` y **rechazó** `set strong-crypto enable` con **`command parse error` / código -61**. Por lo tanto, **NO se afirma que `strong-crypto` esté habilitado**. En su lugar se aplicó y comprobó `ssl-static-key-ciphers disable`. En la **matriz final actualizada** se sustituyó el control original por ese otro, que **no es equivalente**. Por eso se conservan los informes de **17/21 y 20/21 con matriz inicial** y el de **21/21 con matriz revisada**. El 21/21 no debe compararse como cumplimiento de exactamente los mismos 21 controles que en el primer reporte.

[**Leer cronología y explicación técnica completa**](docs/RESULTADOS_COMPARATIVOS_3_DISPOSITIVOS.md) · [**Ver los 5 informes auténticos de la nueva fase**](docs/informes/fase_tres_dispositivos/).

## 7. Evidencias, configuraciones y documentación

| Recurso | Contenido |
|---|---|
| [Documentación técnica ACTUALIZADA en Word](docs/Documento_Tecnico_CIS_Hardening_3_Dispositivos.docx) | Informe integral extenso con capturas, scripts, configuraciones y anexos de los tres dispositivos |
| [Resumen técnico en PDF](docs/Documento_Tecnico_CIS_Hardening_3_Dispositivos.pdf) | Resumen complementario; el documento Word es el informe integral |
| [Documento técnico Cisco original en Word](docs/Documento_Tecnico_CIS_Hardening_Jose_Miguel_Diaz_Ferreras.docx) | Original completo, sin modificaciones |
| [Documento técnico Cisco original en PDF](docs/Documento_Tecnico_CIS_Hardening_Jose_Miguel_Diaz_Ferreras.pdf) | Original completo, sin modificaciones |
| [TODAS las evidencias en una sola carpeta](images/evidencias/) | Capturas originales Cisco, FortiGate, topología final, diagramas y auditoría de demostración 16/21 |
| [Running-config R1 saneado](configs/R1_running-config_final_sanitizado.txt) | Configuración Cisco sin hashes |
| [Running-config SW saneado](configs/SW_running-config_final_sanitizado.txt) | Configuración Cisco sin hashes |
| [Extractos FortiGate verificados](configs/FortiGate_fragmentos_verificados_sin_credenciales.txt) | Configuración documentada de interfaces, objetos, política y hardening; no backup integral |
| [Matriz de requisitos actualizada](docs/MATRIZ_REQUISITOS_ACTUALIZADA.md) | Estado de cada requisito y pendientes |
| [Guion del video completo](docs/GUION_VIDEO_COMPLETO_3_DISPOSITIVOS.md) | Narración completa de ~8 minutos y pantalla sugerida |
| [Cómo subir a GitHub NUEVO](docs/GUIA_NUEVO_REPOSITORIO_GITHUB.md) | Instrucciones para crear el repositorio sin borrar el anterior |

## 8. Precauciones, alcance y pendientes

- Material de simulación académica, **no certificación CIS** ni configuración recomendada sin adaptación a producción.
- Los algoritmos de compatibilidad SSH con IOS antiguo representan una excepción del laboratorio; no recomendamos degradar seguridad real.
- No se incluyen contraseñas, secretos, claves privadas ni imágenes propietarias de Cisco/Fortinet. Revisa cualquier archivo nuevo antes de publicarlo.
- **La evidencia de FortiGate no es un `running-config` integral**; los fragmentos verificados están claramente etiquetados.
- **Video nuevo pendiente**: el enlace del video viejo es únicamente de Cisco. Grabar el nuevo con [el guion](docs/GUION_VIDEO_COMPLETO_3_DISPOSITIVOS.md), publicarlo en YouTube y ponerlo al comienzo del README.

---

**Licencia/aclaración:** Este repositorio documenta una práctica GNS3 autorizada y no incorpora firmware de fabricantes ni materiales restringidos.
