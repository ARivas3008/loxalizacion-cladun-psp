# F2 — Fe de erratas SHA-256 y snapshot PSP RAM (21/11/2026)

**F2 ABIERTA.** Este relevo encontró un error de documentación, no del algoritmo del parcheador: varios informes, notas y prompts recogían 62 caracteres en lugar de los 64 reales del SHA USA. Las constantes de `tools/f2_auditar_origen_iconos.py`, `tools/f2_ram_provenance_1204.py` y `tools/font_es_patch.py` YA eran correctas y no cambiaron.

Se extrajo de nuevo con libarchive el 7z del usuario en el entorno privado, sin alterar la ISO. Tamaño verificado: 305496064 bytes. SHA-256 correcto de 64 caracteres:
`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`

En el offset absoluto 114723840 (0x06D68C00), los 2480 bytes de KITAJIMA_KARI.IMY dieron SHA-256 `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`.

Se corrigieron las referencias documentales 62→64 sin alterar otras métricas históricas. El nuevo `tests/test_f2_sha256_references.py` comprueba mediante AST las constantes de las herramientas y recorre los archivos de texto de docs/reports/prompts/tools/tests/patcher/.github; CI debe rechazar que reaparezca la versión truncada. No se publicaron ISO, BPS ni materiales comerciales.

Se corrigió `tools/f2_ram_provenance_1204.py` para ejecutar `--scan-ram` solo con CPU detenida y ticks de emulación iguales antes/después. La herramienta reanuda únicamente las pausas que provocó. Ante un watchpoint que se detiene por una razón ajena a la dirección vigilada, conserva la pausa del operador. Se ejecutaron 13 pruebas locales sintéticas de la sonda (10 anteriores + 3 nuevas), todas PASS; los controles continuarán por GitHub Actions.

**NO PROBADO:** PPSSPP oficial 1.20.4 real no está disponible, ISO F1 canónica privada no existe en este entorno y curl/git desde el contenedor fallan por DNS. No hubo nueva captura PNG, dump GE real, PC MIPS de iconos, transferencia VRAM, QA visual multicontesto de los 19 glifos ni regresión F1 960×544. Las cifras F1 756/764 son históricas, no de esta ejecución. PR #7 sigue DRAFT. white_new_ink=False y --event-safe-only permanecen intactos.

Informe JSON: `reports/RESULTADO_F2_SHA256_SNAPSHOT_RAM_2026-11-21.json`. El siguiente relevo autónomo completo está en `prompts/SIGUIENTE_TAREA.md` y debe regenerarse recursivamente.
