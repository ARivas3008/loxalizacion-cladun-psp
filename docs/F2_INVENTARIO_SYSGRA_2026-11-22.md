# F2 — Inventario reproducible de 27 recursos SYSGRA.ARC (22/11/2026)

**ESTADO: F2 ABIERTA.** La evidencia siguiente procede de un análisis binario real de la ISO USA original que aportó el usuario, NO de ejecutar Cladun en PPSSPP ni de examinar GPU/VRAM en vivo.

## ISO y recurso original autenticados

Se extrajo de nuevo el archivo de **305496064 bytes** del 7z privado con libarchive. SHA-256 exacto:
`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`

Se inspeccionó DATA.DAT en offset ISO `113770496` y `SYSGRA.ARC` (PSPFS índice `225`, offset local `895488`, longitud `93696`). SHA-256 del SYSGRA ORIGINAL:
`63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854`

DSARC contiene **27 recursos IMY**, cada uno con nombre, tamaño, offset, geometría de cabecera y SHA-256 diferenciados: **27 SHA distintos**. Se confirma `KITAJIMA_KARI.IMY` índice `17`, longitud `2480`, offset DSARC `57856`, offset ISO absoluto `114723840`, SHA-256 `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`. El offset ISO no es RAM/VRAM.

## Pistas para localizar iconos HUD y combate

Se identifican **12 nombres sugerentes**: `HP_BAR.IMY`, `HP_KAO0.IMY`, `HP_KAO1.IMY`, `HP_KAO2.IMY`, `LVSP.IMY`, `LVSP_NUM.IMY`, `DAMAGE.IMY`, `EXP_BAR.IMY`, `MAHO_BAR.IMY`, `MAHO_ST.IMY`, `SYS1.IMY`, `ZOKUSEI.IMY`. Son **candidatos por nombre**, NO recursos cuya aparición en pantalla haya sido autenticada. El resto de 15 miembros se conservó también en el inventario privado sin afirmar su contexto funcional.

La herramienta nueva `tools/f2_inventario_sysgra_usa.py` falla ante ISO incorrecta, recuento PSPFS/DSARC inválido, miembros malformados, nombres duplicados, solapamientos de bytes, cabeceras IMY imposibles o firma de KITAJIMA distinta. Solo exporta metadatos, nunca texturas, paletas ni bytes comerciales. Su informe íntegro con 27 filas se produjo **independientemente** contra la ISO original en carpeta privada: SHA-256 del JSON `b468a11f679f284979d9257bc58e9bc553fdd249940537fd4f745a3fa6b920eb`.

## Pruebas, modificaciones y límites

Commit de código: `bf5fa79a27f889e2391ff7d40b6b56c8bb7e28ca`, junto a `tests/test_f2_inventario_sysgra_usa.py` con **8 pruebas nuevas sintéticas**. GitHub Actions de código `45039311711` push y `45039317909` PR terminadas SUCCESS: **221 tests Python**, verificación de integridad del corpus, tests Go y compilación pública Windows. La comprobación binaria independiente no se confunde con un test PPSSPP.

La terminal no resolvió github.com: `git fetch origin` falló por DNS; se publicó mediante conector GitHub con SHA esperado y sin force push. No se encuentra PPSSPP oficial 1.20.4 en el contenedor ni la ISO F1 canónica. Ningún PNG de juego, dump GE, PC nuevo de iconos ni destino VRAM demostrado. **19 glifos multicontesto y F1 960×544 siguen sin comprobarse aquí**.

No se modificaron corpus canónico, fuentes, integrador, ISO original, BPS ni ajustes `white_new_ink=False` y `--event-safe-only`. PR #7 continúa DRAFT. El nuevo relevo recursivo completo está en `prompts/SIGUIENTE_TAREA.md`.
