# Informes de la integración FortiGate

- `fortigate_auditar_20261112_125624.json`: firewall 3/7 inicial.
- `tres_dispositivos_auditar_20261112_131941.json`: tres dispositivos 17/21 inicial.
- `tres_dispositivos_aplicar_20261112_132403.json`: después de automatización, 20/21; contiene error -61 de `strong-crypto`.
- `tres_dispositivos_auditar_20261112_133434.json`: ejecución intermedia **parcial**, 13/14, no usar para indicar cumplimiento de tres equipos.
- `tres_dispositivos_auditar_20261112_134835.json`: auditoría final 21/21 **con matriz revisada** (sustituido strong-crypto por cifrados TLS estáticos deshabilitados).

El script principal crea nuevos informes en `scripts/informes/` cuando se ejecuta desde este repositorio. Se ignoran en `.gitignore` hasta revisar y seleccionar el archivo adecuado para publicar.
