# CLADUN ES — F3-R6: 11 traducciones españolas de longitud fija simuladas sobre SCRIPT.DAT auténtico (23/11/2026)

**Resultado importante, alcance delimitado:** se comprobó la compatibilidad **estructural** de las 11 traducciones de demo1001 que conservan la misma longitud que el texto original. Se aplicaron **únicamente a bytes privados en memoria** procedentes de la ISO USA original. **NO se reconstruyó ni publicó una ISO, NO se insertaron 85 textos distintos de longitud, NO hubo PPSSPP este relevo, NO se ha verificado aún semántica MIPS.** F2/F3 y F4–F6 siguen abiertas.

## A — experimento verdadero con el usuario ISO original y el borrador GitHub

- ISO original 305.496.064 B, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. Original inmutable.
- Se extrajo a memoria de ISO9660/PSPFS 231 `SCRIPT.SDT` (IMY comprimido ocho bloques) el DSARC `SCRIPT.DAT` (633.344 B, SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`) y `SCRIPT.TBL` (52.016 B, SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`).
- Se reparsearon **1.625 bloques, 51.705 comandos, 46.308 no textuales**; demo1001 corresponde a siete bloques/878 comandos con 97 cadenas no vacías que suman 2.728 bytes origen.
- Del borrador GitHub **real**, blob SHA1 `400a9c9ec06f7456b5ec6e11f7502d711b0a976e`, se extrajeron 11 filas de traducción **exactamente del mismo tamaño**. Para cada una se cotejó su offset original, `bytes_hex`, ID de script y nuevo tamaño tras codificar español en CP932 especial A1–B3.
- Los cambios se hicieron en una `bytearray` privada de `SCRIPT.DAT`, sin guardar sus bytes en el disco; la tabla original se mantuvo sin modificar. La huella del contenido virtual en memoria fue `f042e862cb0f47f4a172ab28872fe9d412d4b0c5f5cf6041b162a39e5531eee9` (NO es fichero publicado).
- **Comprobación integral posterior**: reparseo de los 51.705 comandos, identidad de todos sus offsets, bloques, órdenes, opcodes e IDs; **46.308 payloads no textuales byte idénticos**. Exactamente 11 campos de texto cambiaron, sumando **211 bytes de valor distinto**; ningún byte externo a esos 11 campos se modificó; 1.625 inicios de bloque y tabla TBL intactos; **0 offsets movidos**. Tres bloques afectados: 758, 760, 762. Se conservaron los otros 86 textos no vacíos del demo1001 y todos los restantes textos.
- Estas comprobaciones **no afirman** seguridad semántica de saltos indirectos, referencias de recursos, codificación visual de glifos, eventos en PPSSPP ni validez de un parche final. Es únicamente una base de integración controlada para revisión futura.

## B — herramientas reproducibles, sintéticos y corpus original real en CI

Nuevos `tools/f3_simular_intro_mismo_tamano.py`, `tests/test_f3_simular_intro_mismo_tamano.py`. La herramienta usa interfaces auténticas del repo: `f3_anclar_intro.read_draft/load_geometry/evaluate_rows`, `f3_referencias_riesgo.original_script_children`, `script_event_guard.read_commands/audit_script_rebuild(require_fixed_offsets=True)`. La función de preparación comprueba SHA del blob del borrador de 9.237 filas, las 97 fuentes ancladas y el codec español. El modo sin ISO ejercita el plan **B** con el CSV real, pero NO dice haber hecho simulación ISO. El modo `--iso-original` autentica la ISO, compara el ancla completa de origen y aplica 11 ediciones **solo en memoria** con todas las guardas, reportando únicamente métricas y hashes.

Se crearon **15 tests sintéticos y de integración pública** (incluido el CSV real de GitHub), que deben confirmarse en CI del commit publicado, sin imagen comercial en los runners.

~~~
# CHECKOUT REAL, sin ISO, comprueba el plan ligado al CSV original y ancla:
python tools/f3_simular_intro_mismo_tamano.py
python -m unittest discover -s tests -p 'test_f3_simular_intro_mismo_tamano.py' -v

# ISO AUTÉNTICA solo en ubicación privada; produce METADATOS JSON, NO SCRIPT.DAT:
python tools/f3_simular_intro_mismo_tamano.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/F3_SIMULACION_11_ORIGINAL_NUEVO.json
~~~

## F3 bloqueada más allá de los 11

Los **85** mensajes demo1001 de tamaño distinto generan una deriva hipotética de **588** offsets de comandos en siete bloques, según auditoría F3-R5, con +131 bytes netos de texto si se concatenan sin resolver padding y referencias. No moverlos: falta interpretación real MIPS y referencias externas. Los **4.524** cambios globales siguen bajo `--event-safe-only`. Los 11 candidatos estáticos no están aprobados para publicar BPS o ISO; una traducción estructuralmente válida aún puede no caber visualmente o resultar incompatible con reglas ocultas del motor.

## Bloqueo PPSSPP (C), F2 y continuidad

La AppImage oficial `PPSSPP-v1.20.4-anylinux-x86_64.AppImage` no se encontró; terminal curl falló por DNS `github.com` y descarga alternativa falló. No se obtuvieron capturas, PCs MIPS, WebSocket, GE/VRAM ni QA visual de los 19 glifos durante este relevo. No deben atribuirse al experimento estático.

F2 conserva comparación X11 **A/B/A** (sin sesión real de combate) y la constatación que una sonda de CLUT2 recolorea 9.144 texeles del atlas TUIKA, 3.506 en subregiones protegidas; no usarla como parche final. Mantener `white_new_ink=False`, 2.721 glifos originales, 19 nuevos A1–B3, corpus 9.237 filas, 349 PSPFS, rama `integracion-eventos-segura-20261120` y PR #7 OPEN/DRAFT.

**Próximo:** C real en PPSSPP 1.20.4 con ISO/PPSSPP PID/socket/FD autenticados, A/B/A TUIKA en combate y 19 glifos multicontesto, más inspección dinámica del intérprete que autorice eventualmente los 85 eventos. Si sigue inaccesible, añadir solo instrumentación segura y pruebas sintéticas sin declarar fases cerradas. Continuar regeneración recursiva de `prompts/SIGUIENTE_TAREA.md` hasta F2–F6 verdaderamente completadas.
