# Informes originales y ampliación FortiGate

## Fase 1 — Router Cisco + Switch Cisco (sin modificaciones)

Archivos JSON originales exactos, conservados en esta carpeta:

- [`auditar_20261110_202713.json`](auditar_20261110_202713.json): auditoría inicial Cisco 8/14.
- [`aplicar_20261110_203828.json`](aplicar_20261110_203828.json): aplicación de hardening Cisco.
- [`auditar_20261110_204226.json`](auditar_20261110_204226.json): auditoría final Cisco 14/14.
- [`resumen_verificado_por_capturas.json`](resumen_verificado_por_capturas.json): resumen documental original.
- [README Cisco sin cambios](README_CISCO_ORIGINAL.md): instrucciones originales.

## Fase 2 — Router + Switch + FortiGate

Abrir [`fase_tres_dispositivos/`](fase_tres_dispositivos/) para los cinco JSON obtenidos del Kali exportado en GNS3. Ver [cronología explicada](../RESULTADOS_COMPARATIVOS_3_DISPOSITIVOS.md) para distinguir 17/21, 20/21 y 21/21 con el control alternativo criptográfico.

Ningún reporte fue fabricado; se conserva la incidencia del comando `strong-crypto` no reconocido.
