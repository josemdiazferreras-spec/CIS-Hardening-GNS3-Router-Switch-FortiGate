# Recomendaciones de seguridad elegidas

## Referencias metodológicas

- [CIS Benchmarks para Cisco](https://www.cisecurity.org/benchmark/cisco): catálogo de benchmarks; la versión específica de IOS 15.2 de este laboratorio puede requerir consultar el archivo histórico de CIS.
- [Cisco — Harden IOS Devices](https://www.cisco.com/c/en/us/support/docs/ip/access-lists/13608-21.html): pautas de administración, SSH y `exec-timeout` para IOS.

**No se inventaron numeraciones de controles CIS.** Este trabajo selecciona siete comprobaciones académicas inspiradas en buenas prácticas; se requiere consultar la edición concreta del CIS Benchmark para asignar identificadores normativos exactos.

| ID interno | Regla verificada por script | Importancia | Acción en modo `aplicar` |
|---|---|---|---|
| HTTP-01 | Deshabilitar `ip http server` | Evitar una superficie de administración HTTP innecesaria | `no ip http server` |
| HTTPS-02 | Deshabilitar HTTPS administrativo **si no se necesita** | Reducir servicios de administración expuestos; HTTPS no es inseguro por definición | `no ip http secure-server` |
| CON-03 | `exec-timeout` entre 1 y 10 min | Desconexión de consola inactiva | `exec-timeout 5 0` en `line con 0` |
| VTY-04 | `exec-timeout` entre 1 y 10 min | Desconexión de sesiones SSH inactivas | `exec-timeout 5 0` en `line vty 0 4` |
| SSH-05 | SSHv2 habilitado | Evitar SSHv1 | Solo audita; habilitado durante preparación |
| VTY-06 | `transport input ssh` | Restringir Telnet y otros transportes de texto claro | Solo audita; habilitado durante preparación |
| AUTH-07 | `login local` | Autenticar con usuarios locales | Solo audita; habilitado durante preparación |

## Resultados observados

| ID | R1 antes | R1 después | SW antes | SW después |
|---|---|---|---|---|
| HTTP-01 | Cumple | Cumple | No cumple | Cumple |
| HTTPS-02 | Cumple | Cumple | No cumple | Cumple |
| CON-03 | No cumple | Cumple | No cumple | Cumple |
| VTY-04 | No cumple | Cumple | No cumple | Cumple |
| SSH-05 | Cumple | Cumple | Cumple | Cumple |
| VTY-06 | Cumple | Cumple | Cumple | Cumple |
| AUTH-07 | Cumple | Cumple | Cumple | Cumple |

## Consideraciones

El uso de `Paramiko 3.5.1` para compatibilidad con algoritmos SSH antiguos es una **limitación del entorno**, no hardening. `no aaa new-model` permaneció fuera de los siete controles; no se afirma un cumplimiento AAA general. `no service password-encryption` en SW se había observado inicialmente, pero no fue evaluado por este script de siete reglas. Una evaluación CIS integral requeriría más controles y la edición del benchmark correspondiente.
