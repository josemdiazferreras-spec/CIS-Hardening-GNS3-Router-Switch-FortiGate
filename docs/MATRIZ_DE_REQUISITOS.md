# Matriz de cumplimiento de la asignación

| Requisito docente | Evidencia en este proyecto | Estado |
|---|---|---|
| Repositorio GitHub | ZIP organizado y script previamente subido por estudiante | Estructura preparada; publicación final pendiente |
| Documentación profesional | `README.md` y `docs/DOCUMENTO_TECNICO.md` | Preparada |
| Video demostrativo al principio | [Video en YouTube](https://youtu.be/4RRuTz3-xdg) enlazado al inicio del README | Enlace incluido; pendiente verificar en el repositorio publicado |
| Imágenes | `images/evidencias/` con todas las capturas y diagramas | Incluidas |
| Diagramas | PNG unificados en `images/evidencias/`; fuentes DOT en `docs/fuentes_diagramas/` | Incluidos |
| Propósito del laboratorio | README y documento técnico | Incluido |
| Scripts | `scripts/cis_hardening.py` y `exportar_configuraciones.py` | Incluidos |
| Running-configs finales | `configs/R1_running-config_final_sanitizado.txt` y `configs/SW_running-config_final_sanitizado.txt` | Incluidos, con hashes de contraseña omitidos |
| Topología con equipo elegible | Cisco R1, Cisco SW y Kali en GNS3 | Verificado |
| Herramienta de análisis basado en CIS | Script propio Python/Netmiko con siete controles | Verificado; alcance acotado, no CIS-CAT |
| Hardening aplicado | Deshabilitar HTTP/HTTPS no requeridos y `exec-timeout` | Verificado |
| Explicar recomendaciones y motivos | `docs/RECOMENDACIONES_Y_CIS.md` | Incluido |
| Probar recomendaciones | Auditoría posterior 14/14 e ICMP 5/5 a ambos equipos | Verificado |
| Informe sin reglas aplicadas | `auditar` y captura 8/14 | Verificado; JSON original incluido en `docs/informes/` |
| Aplicación de reglas e informe posterior | `aplicar`, capturas y JSON generado en Kali | Verificado; JSON original incluido en `docs/informes/` |

Se distingue expresamente entre evidencia comprobada, materiales incluidos y archivos pendientes para no afirmar una entrega completa antes de tiempo.
