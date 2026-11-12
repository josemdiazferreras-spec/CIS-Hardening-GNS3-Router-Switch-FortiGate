# Running-configs del laboratorio CIS Hardening

- `R1_running-config_final_sanitizado.txt` y `SW_running-config_final_sanitizado.txt` documentan los **estados finales reales** que el estudiante proporcionó después de aplicar el hardening.
- Ambos archivos son **copias documentales saneadas**: se ocultaron hashes de contraseñas. En SW se omitió además el texto de licencia repetido en banners de IOSv.
- **No son copias aptas para restaurar directamente** mediante `copy` o `configure replace` debido a los marcadores de redacción y omisiones intencionales.
- `R1_extracto_original_antes_de_SSH.txt` y `SW_extracto_original_antes_de_SSH.txt` son extractos parciales previos a la preparación del acceso SSH; no se deben describir como running-configs iniciales íntegros.
- La auditoría JSON inicial se hizo **después** de habilitar SSH para la automatización.
- No publicar hashes, contraseñas, claves privadas, comunidades SNMP ni imágenes propietarias de Cisco.
