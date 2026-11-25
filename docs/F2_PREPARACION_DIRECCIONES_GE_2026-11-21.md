# F2 — Preparación de direcciones GE, no traza funcional (21/11/2026)

**Estado:** F2 ABIERTA. No hay ejecución nueva del juego en PPSSPP oficial 1.20.4; el AppImage oficial no existe localmente y su descarga falló. La ISO F1 canónica tampoco está disponible. La ISO USA original sí se inspeccionó y autenticó en esta sesión.

## 1. Auditoría binaria auténtica

- ISO privada USA: 305496064 bytes; SHA-256 de 64 caracteres: `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- Recurso iconos CONTROLES KITAJIMA_KARI.IMY: lectura de 2480 bytes desde offset ISO 114723840 (0x06D68C00), SHA-256 `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`. El offset ISO NO es dirección RAM.
- El analizador de atlas original ejecutado de nuevo sobre esa ISO devolvió 19 glifos, 2721 registros originales, 100 texels de tinta optativa. SHA-256 del JSON nuevo `88edb8a2cf1a920f1ff7480cbe4b06f44d5441a1183720b71a07b393a49bfb80`, idéntico al precedente. Se ejecutaron 18 tests locales de los lectores antiguos: PASS. Es QA ESTÁTICA, no PPSSPP.
- Manifiesto de verificación privada, sin material comercial, SHA-256 `d105cec882bfbc2e6dd7e4ac2f41aad0717cbf2eac0abd6a1325892b7f3cb178`.

## 2. Ampliación real del lector GE

Modificado `tools/f2_ge_dump_1204.py` y añadido 4 pruebas en `tests/test_f2_ge_dump_1204.py`. Las fórmulas provienen exactamente de `GPU/GPUState.h`, `GPU/ge_constants.h` y `GPU/Debugger/RecordFormat.h` del tag oficial `hrydgard/ppsspp/v1.20.4`:

- texturas (niveles 0–7): `(TEXADDR[level] & 0xFFFFF0) | ((TEXBUFWIDTH[level] << 8) & 0x0F000000)`.
- CLUT: `(CLUTADDR & 0x00FFFFF0) | ((CLUTADDRUPPER << 8) & 0x0F000000)`.
- transferencia src/dst: `(TRANSFERxx & 0xFFFFF0) | ((TRANSFERxxW & 0xFF0000) << 8)`.
- geometría transferencia desde TRANSFERSIZE y bytes/píxel de TRANSFERSTART.

Las entradas `REGISTERS` de una grabación PPSSPPGE v6 permiten ahora el campo `ge_address_candidates_limited_to_150`, con posición de recorder/word y los valores numéricos de registros observados. Otro campo cuenta todos los triggers aunque se limiten los ejemplos a 150. La bandera `in_primary_2mib_vram_window` indica solo si una cifra cae en el rango típico `0x04000000–0x041FFFFF`, NO demuestra que se haya transferido un recurso ni que allí estén los iconos. El estado inicial de GPU podría faltar: NO se asumen registros no observados. Jamás confundir candidato con traza RAM→GE→VRAM.

## 3. Tests, CI y límites

Commit de código `161dcec70731e0472c5418547074d5a5d08c110f`. GitHub Actions sobre ese HEAD: push `44987146237` y PR `44987149980`, ambos SUCCESS; **213 tests Python** PASS, verificación del corpus e integrabilidad, Go y compilación pública Windows PASS. Ninguna ISO ni dump comercial publicados.

Bloqueos: PPSSPP 1.20.4 AppImage ausente; acceso a `github.com` desde shell falló por DNS, descarga oficial no posible; ISO F1 canónica ausente. Nueva captura PNG: **0**; nuevos GPU dumps: **0**; PC de iconos comprobados: **0**; direcciones VRAM de juego comprobadas: **0**; 19 glifos PPSSPP multicontesto: **NO PROBADO**; regresión F1 960×544 nueva: **NO PROBADO**. Mantener PR #7 DRAFT, 4524 textos SCRIPT.DAT aplazados, `white_new_ink=False` y el escudo `--event-safe-only`.

Informe estructurado `reports/RESULTADO_F2_DIRECCIONES_GE_2026-11-21.json`. Estado y relevo recursivo `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y `prompts/SIGUIENTE_TAREA.md`.
