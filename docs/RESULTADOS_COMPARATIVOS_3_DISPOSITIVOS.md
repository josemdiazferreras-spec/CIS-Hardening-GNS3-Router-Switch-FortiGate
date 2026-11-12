# Cronología verificable: Cisco original + FortiGate añadido

**No se han sobrescrito ni reemplazado las evidencias de la primera fase.** Son dos fases sucesivas con matrices diferentes.

| Fase | Matriz | R1 | SW | FortiGate | Total | Archivo |
|---|---|---|---|---|---|---|
| A — Auditoría inicial Cisco | 7+7 | 5/7 | 3/7 | No añadido | **8/14** | `docs/informes/auditar_20261110_202713.json` |
| A — Auditoría final Cisco | 7+7 | 7/7 | 7/7 | No añadido | **14/14** | `docs/informes/auditar_20261110_204226.json` |
| B — Auditoría de 3 equipos, sin cambios nuevos | 7+7+7 (control strong-crypto) | 7/7 | 7/7 | 3/7 | **17/21** | `docs/informes/fase_tres_dispositivos/tres_dispositivos_auditar_20261112_131941.json` |
| B — Tras aplicar hardening automatizado | 7+7+7 (control strong-crypto) | 7/7 | 7/7 | 6/7 | **20/21** | `docs/informes/fase_tres_dispositivos/tres_dispositivos_aplicar_20261112_132403.json` |
| B — Revisión intermedia/resultado parcial | solo 14 controles evaluados | parcial | parcial | 6/7 | **13/14 evaluados** | `docs/informes/fase_tres_dispositivos/tres_dispositivos_auditar_20261112_133434.json` |
| B — Auditoría final con matriz alternativa | 7+7+7 (cifrados TLS estáticos) | 7/7 | 7/7 | 7/7 | **21/21** | `docs/informes/fase_tres_dispositivos/tres_dispositivos_auditar_20261112_134835.json` |

**Importante para el profesor:** el valor 21/21 corresponde a la **matriz revisada**, ya que la instancia de FortiOS rechazó `set strong-crypto enable` con código -61. Se sustituyó ese control por la verificación de `ssl-static-key-ciphers disable`, que sí quedó aplicado. Ambos controles están relacionados con criptografía, pero **no son equivalentes**. La comparación preserva los originales para dar trazabilidad.

**Ninguno de los porcentajes anteriores es certificación CIS oficial.**

## Evidencias del trabajo Cisco (se preservan intactas)

1. Topología original: [`../images/evidencias/cisco_01_topologia_gns3_real.png`](../images/evidencias/cisco_01_topologia_gns3_real.png)
2. Pruebas iniciales y Netmiko R1/SW: `images/evidencias/02_...`, `03_...`, `04_...`
3. Auditoría Cisco 8/14: [`../images/evidencias/cisco_05_auditoria_inicial_8_de_14.png`](../images/evidencias/cisco_05_auditoria_inicial_8_de_14.png)
4. Aplicación automática R1 y SW: `images/evidencias/06_...`, `07_...`, `08_...`
5. Auditoría Cisco 14/14: [`../images/evidencias/cisco_09_auditoria_final_14_de_14.png`](../images/evidencias/cisco_09_auditoria_final_14_de_14.png)
6. Ping final 5/5 a R1 y SW: [`../images/evidencias/cisco_10_conectividad_final.png`](../images/evidencias/cisco_10_conectividad_final.png)
7. Running-configs finales saneados: `configs/R1_...`, `configs/SW_...`

## Evidencias nuevas de FortiGate

Topología ampliada, pruebas de Kali, acceso SSH, auditoría inicial 3/7, auditoría conjunta 17/21, aplicación 20/21, auditoría revisada 21/21, informes JSON y transferencia por disco GNS3 están en `images/evidencias/` y `docs/informes/fase_tres_dispositivos/`.
