# CLADUN ES — NUEVO RELEVO AUTÓNOMO F2: GE/VRAM de iconos, QA multicontesto de 19 glifos y regreso F1

Actúa como ingeniero sénior PSP MIPS/GE, PPSSPP 1.20.4, formatos IMY/CLUT, DSARC/PSPFS, CP932, localización española, codificación, BPS y pruebas funcionales. **EJECUTA modificaciones y tests reales**, no solo instrucciones. Mantén la traducción original de Cladun protegida. Al finalizar genera otro prompt completo y autónomo en este mismo archivo, y exige volver a generar otro al terminar la siguiente tarea.

## 1. Repositorio y documentos antes de editar

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: `integracion-eventos-segura-20261120`
PR #7 DRAFT: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base: `revision-manual-dialogos`. **Confirmar HEAD GitHub actual y checks CI** antes de modificar, nunca usar hashes de commit anteriores como HEAD garantizado.

Leer completos:
- `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`;
- `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md`, `docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md`;
- `reports/RESULTADOS_F1_PPSSPP_REAL_2026-11-21.json`, `reports/RESULTADOS_F2_ATLAS_PPSSPP_2026-11-21.json`, `reports/RESULTADOS_F2_ICONOS_TINTA_PPSSPP_2026-11-21.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`;
- `tools/charset_es.py`, `tools/font_es_patch.py`, `tools/font_es_narrow.py`, `tools/auditar_atlas_f2.py`, `tools/generar_probe_f2_indice.py`, `tools/generar_probe_f2_iconos.py`, `tools/generar_probe_f2_glifos.py`, `tools/generar_probe_f2_tinta.py`;
- `tools/menu_layout_es.py`, `tools/integrar_parche_seguro.py`, `tools/generar_parche_bps.py`, tests F1/F2, `qa/`, `traduccion/`.

Nunca publicar ISO, BPS, EBOOT, RAM, FONT.ARC, texturas, PNG comerciales, capturas o ZIP de evidencias en GitHub. Todo eso se mantiene en directorios/entregables PRIVADOS. Ningún artefacto de juego se incorpora al repo.

## 2. Estado comprobado F1 (NO REGRESAR)

ISO original USA 305.496.064 bytes SHA-256:
`b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
ISO F1 canónica española SHA-256:
`496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`.
BPS experimental F1 desde USA SHA-256:
`daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`.
PPSSPP oficial AppImage Linux 1.20.4 SHA-256:
`661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.

F1 Opciones fue aprobada con ventana **960×544** en Xvfb **1280×720**, con borde original **756px interiores / ≈764 exteriores**, y=106, R/G/B>125, x160..1104, valores «Sí/No», cuatro estados decimales, Controles y regreso al título. Etiqueta 005709 diez U+3000 + siete ASCII, No 005713 espacio final solo presentación. **NO cambiar redacción o rellenos F1 ni archivos canónicos sin pruebas y un commit atómico de CSV + 2 TXT + bitácora + vistas.** Los ensayos F2 recientes se hicieron en **fullscreen 1280×720** y NO prueban la cifra histórica 756/764; restaurar geometría precisa al aprobar cualquier nueva fuente.

## 3. Ingeniería inversa F2 — resultados demostrados, NO exagerar

Atlas de fuente USA 2721 glifos; español 2740 al insertar 19 glifos CP932 A1–B3 después del índice 95; los 2721 originales conservan código, métricas y píxeles. En el depurador de PPSSPP se observó acceso MIPS a `FONT.BIN` RAM `0x09075000` y PC `0x089089C8` `lhu t2,0(t1)`, búsqueda código→índice para texto. Sondas sobre posiciones viejas/nuevas de `FONT.ARC` alteraron C, pero iconos de Controles permanecieron idénticos. Esto NO demuestra cómo se cargan todos los iconos.

**TEXTURA DEMOSTRADA PARA ICONOS DE CONTROLES**: `PSP_GAME/USRDIR/DATA.DAT → SYSGRA.ARC → KITAJIMA_KARI.IMY`.
PSPFS `SYSGRA.ARC` índice 225, offset 895488 en DATA.DAT; DSARC `KITAJIMA_KARI.IMY` índice 17/27, offset 57856 en ARC, longitud 2480, SHA preimagen `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`. `tools/generar_probe_f2_iconos.py` cambió únicamente **27 bytes RGB de la paleta** (alpha, datos de textura e índices intactos); los **348 recursos PSPFS** vecinos y 26 miembros DSARC ajenos quedaron byte-idénticos.
ISO F2 diagnóstica CLUT magenta SHA `b634fe468158a7ba5c3242896d4b1c43e711de53a19869c3b469a4877bc2e73d`. BPS diferencial **F1→magenta**, NO desde USA, SHA `4b0a47d9ff2b33f364be45f508ab4510776c0bb6b4cc7245236699c5fbe25c61`, roundtrip exacto.
En PPSSPP real los iconos R/□/×/○/△/L se volvieron magenta (1136/1360/1353/1353/1337/1143 píxeles cambiados); **texto de acciones 0 y borde 0**. **Falta identificar el PC MIPS de la carga, buffer RAM, comandos GE y VRAM y repetir HUD/tutoriales/combate**; no confundir causalidad del recurso en Controles con el seguimiento de la ruta completa.

**ERROR REAL DE TINTA DE 19 GLIFOS:**
- Diagnóstico `tools/generar_probe_f2_glifos.py` crea CSV privado 9237 registros, cambia únicamente el texto 005694 a `F2 áéíóú ÁÉÍÓÚ ñÑüÜ ¿¡ «» ō` y overrides de rellenos F1 005709/005713. Corpus/TXT canónicos intactos. CSV SHA `800709d105a86e6da3252c44e4a2138fa8fec01e51afd0283e27913d272f1f7e`.
- ISO amarilla del diagnóstico desde USA SHA `58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca`; BPS desde USA `a95039e13f9ace10d7b14f7a2587c0297c4889bf5f87a0263da289d6cc40f971`, roundtrip exacto.
- El CLUT de `FONT_00.IMY` tiene índice15 RGB(247,247,0) amarillo e índice1 RGB(255,255,255) blanco; `make_glyph` agregaba píxeles índice15. `font_es_narrow.patched_archive_narrow(...,white_new_ink=True)` convierte **100 texels 15→1 SOLO de los 19 glifos nuevos** preservando los 2721 glifos originales, FONT.BIN y 348 PSPFS ajenos. **False es el valor por defecto para congelar F1**.
- `tools/generar_probe_f2_tinta.py` produce ISO privada blanca SHA `a42731988835bddb9dc81ef6d242b9c5029030256f210838881a1d48aed2de33`; BPS **amarilla→blanca**, NO desde USA, SHA `2a698e1efaa1c2333dbd86ac8c3a9fabbd369382c4b8c7d3ad0ab7c7f2ffac3f`, roundtrip exacto.
- PPSSPP real con dos PNG crudos por variante: en ayuda ROI x40..700 y624..700, RGB amarillo R>180,G>170,B<80: **516→0**. Tinta corregida en esa escena, pero **los 19 caracteres NO tienen todavía QA individual de espaciado/márgenes/recorte en escenas reales múltiples**. F2 ABIERTA.
- ZIP privado de esta sesión `Cladun_ES_F2_Iconos_Tinta_19Glifos_PPSSPP_2026-11-21_EVIDENCIAS_PRIVADAS.zip`, SHA `af93e1d702d1d53d10d9fcfb326030c1a62cfb7c4ea4482846d7f26a83c49cad`, 9 PNG reales con SHA en manifiesto. NUNCA subir ZIP/PNG a GitHub.

## 4. Objetivos técnicos de la siguiente ejecución (OBLIGATORIOS)

**A. Completar la ruta MIPS y GE/VRAM del recurso:**
1. Carga PPSSPP real (WebSocket debugger local `ws://127.0.0.1:24192/debugger`, subprotocolo `debugger.ppsspp.org`) con ISO F1 autenticada y sondeos privados.
2. Traza `SYSGRA.ARC/KITAJIMA_KARI.IMY` desde lectura/descompresión, buffer RAM, subida a GE y textura VRAM, y el draw de iconos. Documenta **dirección PSP, PC MIPS, opcodes, offsets de archivo y llamadas reales**. Si no se pueden demostrar, mantener «no demostrado» y continuar sin inventar.
3. Repite sondas positivas/negativas con capturas para iconos de HUD, tutoriales, ayuda, diálogos, combate. Nunca asumir que usan KITAJIMA solo porque Controles lo usa.

**B. Auditar todos los glifos españoles en varias escenas reales:**
1. Identifica escenas con `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`. Examina ancho/avance, anclaje, superposición de diacríticos, signos iniciales, comillas, márgenes e interacción con símbolos L/R/PSP.
2. Obtén mínimo dos PNG `scrot` SIN editar por escena/estado, registra SHA individuales. Si faltan caracteres en corpus visible, genera texto **solo en variante CSV/ISO privada** con `--borrador --experimental-parcial --event-safe-only`.
3. Si el opt-in blanco funciona en TODOS los contextos, integra deliberadamente en un commit independiente, prueba antes/después, repite F1 geometría960×544 y compara SHA ISO/BPS; si fallan las pantallas, NO adoptarlo. El estado actual es solo experimento, no publicación.

**C. Integridad, BPS, CI y pruebas:**
```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
```
Para ISO canónica desde USA autenticada:
```bash
python tools/integrar_parche_seguro.py --iso "$ISO_USA" --candidate "$ISO_CANDIDATA" --report "$REPORTE" --experimental-parcial --event-safe-only
python tools/generar_parche_bps.py --original "$ISO_USA" --candidato "$ISO_CANDIDATA" --informe-integracion "$REPORTE" --salida "$BPS_PRIVADO" --informe-bps "$BPS_REPORTE" --experimental --event-safe-only
```
Para overlay de glifos generar CSV privado primero y agregar `--borrador "$CSV_PRIVADO"` a integración, nunca al borrador canónico; la ISO resultante debe autenticarse por SHA. Los BPS F2 diferenciales desde F1 o desde ISO diagnóstica **NO** se confunden con parches desde la USA original. Destinos nuevos, sin sobrescritura. Exigir roundtrip BPS bit a bit.

Verificar 349 PSPFS, 345 recursos no textuales ajenos a cuatro contenedores de integración, DSARC/ISO9660 ajenos, 51.705 comandos, 46.308 no textuales y 1.625 scripts sin mover offset, **4.524 traducciones aplazadas**. Nunca omitir `--event-safe-only`. Para variación FONT.ARC preservar los **otros 348 PSPFS**. Comprobar GitHub Actions del HEAD final: pruebas Python/Go, integridad, integrabilidad y build Windows sin payload. No atribuir imágenes reales a tests unitarios sintéticos.

## 5. Pendientes F3–F6 y condición de publicación

F2 abierta hasta MIPS/GE de iconos y QA completo 19 caracteres; F3 introducción todavía inglesa, F4 modelo seguro de las 4.524 traducciones SCRIPT.DAT aplazadas, F5 nivel/mapa/HUD/tutorial/combate/inventario/retratos/guardado/carga, F6 BPS y ejecutable Windows final y regresión. **Mantener PR #7 DRAFT**, no publicar parche completo ni declarar traducción 100% hasta pruebas.

## 6. ENTREGA Y RELEVO RECURSIVO OBLIGATORIOS

Al terminar: registra lo REALMENTE ejecutado (archivos, PCs MIPS, GE/VRAM, diferencias visuales, 2+ PNG y hashes, ISO/BPS privados, scripts/offsets, logs, CI final, commits y PR). Separa pruebas **estáticas**, **binarias**, **PPSSPP visual** y **gameplay**. Si falta una comprobación, declara F2 **ABIERTA** y documentación del bloqueo.
Actualiza `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y docs. **REESCRIBE COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` con otro prompt AUTÓNOMO que incluya todo el contexto y obliga a generar OTRO al terminar. MUÉSTRALO al usuario.** Repetir recursivamente hasta completar F2/F3/F4/F5/F6, toda la traducción y pruebas de integración.
