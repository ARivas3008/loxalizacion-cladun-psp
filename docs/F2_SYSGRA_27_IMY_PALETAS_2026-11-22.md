# F2 — Auditoría completa de 27 IMY y cuatro variantes de paleta (22/11/2026)

**Estado: F2 ABIERTA.** Nuevo análisis **real de bytes de la ISO USA original** y pruebas sintéticas/CI. No se ejecutó PPSSPP oficial 1.20.4 en este relevo; no se generaron capturas nuevas, dump GE real ni nueva ISO F1. Se conserva la distinción entre análisis de archivo y uso real GPU/VRAM.

## Fuente original autenticada

ISO privada recibida en 7z, **305496064 bytes** y SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. Se autenticó `SYSGRA.ARC` (PSPFS índice 225, offset en DATA.DAT 895488, tamaño 93696 bytes, SHA-256 `63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854`) sin modificar los datos. El auditor valida la entrada de PSPFS, la tabla DSARC de 27 miembros, nombres, rango, no solapamiento y firmas históricas de `FONT.IMY` y `KITAJIMA_KARI.IMY`.

## Descubrimiento binario real: 27 miembros decodificados

Se reconstruyeron en memoria **27 de 27** texturas indexadas IMY con su longitud de salida correcta y sin emitir gráficos comerciales. Hay **24 superficies de índices de píxel únicas**. El esquema original presenta dos variantes documentadas:

| Variante IMY de cabecera | Colores RGBA almacenados | Ubicación de flags | Miembros |
|---|---:|---|---:|
| `0x60` | 16 | `0x0060` | **14** |
| `0x20` | 256 | `0x0420` | **13** |

Las cabeceras de formato `0xA4` aparecen 23 veces, `0x84` cuatro veces. Catorce miembros terminan con dos bytes nulos de alineación y trece sin relleno final. Parte de los flujos de flags contiene 1–3 comandos nulos de alineación tras alcanzar la geometría: se aceptan **únicamente** si sobran hasta tres flags de valor 0; cualquier comando sobrante no nulo, más de tres bytes de flags, relleno final no nulo o exceso de salida provoca error.

## PALETE_0 a PALETE_3: mismo índice, cuatro paletas

`PALETE_0.IMY`, `PALETE_1.IMY`, `PALETE_2.IMY` y `PALETE_3.IMY` tienen la **misma matriz de índices descomprimida** de 512 bytes, SHA-256:

`076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560`

Sin embargo, las cuatro tablas almacenadas de 256 entradas RGBA tienen SHA-256 diferentes: `3c7418b3...`, `b8d7c9bb...`, `e026fd63...` y `fc1b460d...` (completos en informe JSON). Esto demuestra variación de **datos de color** con idéntica geometría de índices; no demuestra en qué pantalla de PPSSPP se selecciona cada paleta.

El recurso `FONT.IMY` conserva SHA de índices decodificados `5d4ff855af1132ea0abf204b5a4c44ddce28b55758772feba21ce6163cc6c4fc`. No atribuir todavía menús, tutorial, HUD, combate o 19 glifos a este recurso por nombre.

## Implementación y pruebas

Nuevo lector de solo lectura `tools/f2_auditar_27_imy_sysgra.py` y `tests/test_f2_auditar_27_imy_sysgra.py` (**25 pruebas sintéticas nuevas**). La prueba privada sobre la ISO auténtica finalizó con 27 miembros, 24 superficies únicas y cuatro paletas diferentes. Evidencia privada **solo de hashes/metadatos**:
`CLADUN_F2_SYSGRA_27_IMY_Decodificados_privado_2026-11-22.json`, tamaño 32673 bytes, SHA-256 `b17966be9d0f3a40570893453f38a5b6a24a52ec928427bc237680bfad24d717`.

Commit de código `70d3aed096f57234fb66038c320cef2e21311b49`. Actions `push 45042960385` y `pull_request 45042967194`: ambas **SUCCESS**, **274 pruebas Python**, tests Go, integridad de corpus/preflight y compilación Windows pública sin BPS. Son pruebas de código, NO ejecución real de Cladun.

## Pendientes sin atribuciones falsas

No hay AppImage PPSSPP en el entorno. `git fetch origin` y `git pull --ff-only` no resuelven `github.com`; el checkout local tampoco tiene referencia `HEAD`. La ISO F1 canónica de SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986` no está disponible. Sin ello: **0 capturas PPSSPP nuevas, 0 dumps GE auténticos, 0 PCs de iconos probados**, los 19 glifos multicontesto NO comprobados y regresión F1 ventana X11 960×544 NO repetida.

No se editaron corpus (9237 registros), 2721 glifos originales, contenedores del juego, integrador, BPS, ISO ni ajustes `white_new_ink=False` / `--event-safe-only`. Se conserva PR #7 **DRAFT**; F3 intro inglesa, F4 4524 textos script, F5 recorrido y F6 BPS/EXE finales continúan pendientes.

Informe: `reports/RESULTADO_F2_SYSGRA_27_IMY_2026-11-22.json`; continuidad `reports/ESTADO_CONTINUIDAD_PPSSPP.json`; siguiente relevo completo `prompts/SIGUIENTE_TAREA.md`.
