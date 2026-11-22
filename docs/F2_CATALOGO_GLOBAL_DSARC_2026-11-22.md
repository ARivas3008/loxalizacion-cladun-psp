# Cladun ES — F2: auditoría integral de los cuatro DSARC de la ISO original (22/11/2026)

**F2 SIGUE ABIERTA.** Solo se ha inspeccionado una ISO privada real, nunca se afirma haber obtenido un nuevo frame PPSSPP. La red de terminal carece de resolución DNS de GitHub, y no hay AppImage PPSSPP 1.20.4 ni ISO F1 canónica autenticada en este contenedor.

## Evidencia original íntegra, no reconstruida

Se verificaron 305496064 bytes de la ISO USA recibida y SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f` (64 dígitos). El recorrido independiente ISO9660 ubicó `DATA.DAT` en offset `113770496` y 349 entradas PSPFS. Los **únicos cuatro contenedores DSARC identificados por cabecera** son:

| Índice PSPFS | Archivo | Miembros | SHA-256 contenedor (bytes almacenados) |
|---:|---|---:|---|
| 0 | `SYS.DAT2` | 6 (PNG) | `208220bf6f1142359f9fb3707f81fd4ecb876b75a5c00bd1c6c1cf82fb6c8175` |
| 188 | `SE.ARC` | 68 (SPS) | `b075dabc58444292c1b23bb2207a935cba3f36e5381a63c48f21e814ad6c5d36` |
| 225 | `SYSGRA.ARC` | 27 (IMY) | `63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854` |
| 308 | `FONT.ARC` | 7 (BIN y IMY) | `420613ae4a16595b00c75d17bfb86290e57a30419d81ddbc6f245035e63c9805` |

**108 miembros DSARC y 108 hashes SHA-256 diferentes**. Se validaron límites y ausencia de solapamientos, cabeceras PNG/IMY/SPS, tamaños, nombres y recuentos. No se exportó ningún archivo original de estos contenedores.

## Hallazgo específico de F2: dos recursos tipográficos independientes

- `SYSGRA.ARC/FONT.IMY` (recurso independiente): SHA-256 `50143c165f10aa71ac77d4a2b09fd69012b1eceac4a102bf8e2b8157bf8b5915`.
- `FONT.ARC/FONT_00.IMY` (página de atlas): SHA-256 `698bc5b398a16c3f2a4615527dac6a36dbae73666a7c45c3787bb00a728a8478`.

**Solo se demuestra que los bytes almacenados difieren.** No se puede inferir contenido visual similar o distinto, ni uso efectivo de fuentes durante juego, ni origen de un contexto particular. Antes de finalizar la QA de 19 glifos, investigar por separado en PPSSPP si SYSGRA/FONT.IMY se usa en HUD/menús y cuál es su relación con FONT.ARC. Los 12 nombres candidatos de HUD/combate del relevo anterior siguen siendo conjeturas por nombre.

## Código publicado, fallo de CI detectado y corrección

Se creó `tools/f2_catalogo_global_dsarc_usa.py` con 12 pruebas sintéticas nuevas en `tests/test_f2_catalogo_global_dsarc_usa.py`. Commit `375eec3d7bcb3dbc878f9579ed49e9af92279091`. El primer CI reveló que un solapamiento podía ocasionar un fallo por cabecera PNG antes de notificarse el conflicto estructural; se corrigió comprobando todos los rangos ANTES de las firmas (commit `822a17dc457ec761a56164db6fdcbc8b7fa8f93d`).

Actions del commit reparado: push `45040317705`, PR `45040322660`, **ambas SUCCESS**. **233 pruebas Python** ejecutadas satisfactoriamente (antes 221), integridad y preflight del corpus PASS, tests Go PASS y compilación pública Windows sin BPS PASS. El CI es real, pero no prueba visual PPSSPP.

El JSON PRIVADO de 108 filas se produjo desde los bytes originales mediante un auditor independiente: `CLADUN_F2_catalogo_DSARC_108_privado_2026-11-22.json`, SHA-256 `9938fd9fc0eba271494ecdfeec49c1ffd95291b0abecdc33ca65ee97c00bc567`. Contiene metadatos y hashes, no texturas.

**NO PROBADO**: traza MIPS→RAM→GE→VRAM; 19 glifos en varios contextos; HUD/combate/testimonios de iconos; ventana X11 960×544 y F1 reciente. **NO GENERADO**: ISO candidata, BPS, PNG PPSSPP nuevo, dump GE real. Invariantes intactas: 349 PSPFS, 345 ajenos a cuatro contenedores, 348 vecinos y 26 DSARC vecinos para sondas aisladas, SCRIPT.DAT 51705 comandos/46308 no textuales/1625 inicios/4524 cambios aplazados. No alterar `white_new_ink=False` ni `--event-safe-only`. PR #7 permanece DRAFT.

Metadatos estructurados: `reports/RESULTADO_F2_CATALOGO_GLOBAL_DSARC_2026-11-22.json`. Continuidad: `reports/ESTADO_CONTINUIDAD_PPSSPP.json`. Prompt de siguiente relevo: `prompts/SIGUIENTE_TAREA.md`.
