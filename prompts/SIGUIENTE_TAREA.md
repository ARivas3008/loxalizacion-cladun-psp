# NUEVA TAREA AUTÓNOMA CLADUN ES — CONTINUAR F2: identificar iconos y validar 19 glifos en PPSSPP real

Actúa como especialista PSP MIPS, PPSSPP 1.20.4, GPU/GE, DSARC/PSPFS, CP932, fuentes IMY, localización española e integridad BPS. **Realiza cambios, experimentos y pruebas auténticas**, no solo instrucciones. No declares F2 cerrada hasta probar **todos** los caracteres y descubrir la procedencia funcional de los iconos en contextos relevantes. **Al finalizar DEBES generar otro prompt completo autónomo y exigir la misma obligación recursiva**.

## Repositorio, límites y lectura

- Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
- Rama: `integracion-eventos-segura-20261120`; PR #7 borrador, base `revision-manual-dialogos`; último código F2 documentado `202ff8d92513106f2e24a193c5032500bcc74c2d` (verificar HEAD en vivo).
- Leer antes de modificar: `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md`, `reports/RESULTADOS_F2_ATLAS_PPSSPP_2026-11-21.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `tools/charset_es.py`, `tools/font_es_narrow.py`, `tools/font_es_patch.py`, `tools/auditar_atlas_f2.py`, `tools/generar_probe_f2_indice.py`, `tools/integrar_parche_seguro.py`, `tools/generar_parche_bps.py` y `tests/test_atlas_f2.py`.
- NO subir ninguna ISO, BPS, EBOOT, FONT, RAM o PNG comercial a GitHub. Mantener `--event-safe-only` y 4.524 traducciones script protegidas. Nunca fusionar el PR sin QA completa.

## Estado congelado F1

F1 Opciones **cerrada** por PPSSPP real (no juego completo). ISO USA 305.496.064 bytes SHA `b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f`; ISO F1 canónica SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`; BPS F1 SHA `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`; PPSSPP oficial AppImage SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. Opciones mide 756 píxeles internos, ~764 exteriores, x342..1097 en fila y106, RGB>125, Xvfb1280×720, ventana960×544, software. 005709 = «Decimales de daño»+10 U+3000+7 ASCII **solo en presentación**; 005710 «Sí», 005713 «No»+1 ASCII de presentación. Preservar esta salida antes/después de F2.

## Evidencia F2 de la última sesión

**Auditoría independiente REAL:** fuente original 2721 glifos, española 2740, 19 glifos A1–B3 insertados índice 95. Los 2721 existentes conservan código, métricas y los 256 píxeles de cada celda. □ CP932 81A0 166→185; ○ 819B 162→181; × 817E 143→162; △ 81A2 168→187. Los ASCII L/R índices 44/50 siguen iguales.

**Depurador PPSSPP REAL:** módulo CLDN_TRIAL base PSP `0x08804000`; tabla FONT.BIN RAM `0x09075000`; PC `0x089089C8` ejecutó `lhu t2,0(t1)` en un bucle de **búsqueda binaria por código de glifo** (registros 4 bytes, rango aprox. 0x089089A0–0x08908A18). El watchpoint real de C detectó **1867 lecturas**; □ y ○ tuvieron 0 lecturas durante Controles, lo que solo acota esa observación. EBOOT en disco `~PSP` cifrado; usar RAM PSP ya cargada, no afirmar ELF de disco.

**Prueba diferencial REAL:** dos ISO privadas sobre la F1 (solo siete celdas de FONT.ARC modificadas C, L, R, □, ○, ×, △; FONT.BIN intacto; 349 PSPFS, 348 vecinos exactos). ISO nueva SHA `77d101111409794e2db25cc4c0eb0707149078416759aa3dd4a3d68db1113b90`; ISO vieja SHA `48cf0228f6084bf3359db534651054960c3c94388bf4afa114b9af493630798d`. BPS PRIVADOS desde **F1**, no USA: nuevos `375750f62421e2f8fd5a40883479e19367e5632b07e9a97ed452e89b434737ac`, viejos `cb29cc5299bf29dde2c311d435fc721b21264eb9aa463af336cde5e9ccefecda`, ambos roundtrip exacto. En dos estados auténticos PPSSPP, **C de Correr/Cambiar cambió a bloque** (504/536 píxeles distintos), pero **los seis iconos R □ × ○ △ L permanecieron exactamente iguales (0 píxeles diferentes)** tanto en la variante vieja como nueva. Resultado acotado a Controles: **no se ha localizado el verdadero recurso de los iconos** y no se puede extrapolar a HUD/tutoriales/combate.

Evidencia privada: `Cladun_ES_F2_PPSSPP_Pruebas_Indices_2026-11-21_EVIDENCIAS_PRIVADAS.zip`, ocho PNG originales scrot y JSON, SHA `a4320955f84210776cd5857ed2174d2f81c437b3cf2ba712e92d4b6764b1c2b8`. CI código F2 `202ff8d` pasó 146 tests Python, Go, corpus e integrabilidad en runs 44959226947/44959222272.

## Primera tarea — rastrear textura de iconos, no suponer

1. Obtén ISO original legítima de usuario y confirma SHA; ejecuta la F1 canónica en PPSSPP oficial, depurador WebSocket local `ws://127.0.0.1:24192/debugger` (protocolo `debugger.ppsspp.org`) o el puerto de la sesión actual. Identifica en RAM texturas/paletas, comandos GE, referencias de VRAM y llamadas de dibujo **mientras Controles renderiza R/□/×/○/△/L**.
2. Demuestra cadena `PSPFS / DSARC / archivo → miembro/offset → textura → carga VRAM → draw call MIPS` con referencias reproducibles. Comparar con FONT.BIN y old/new sondas. Probar con modificación única en ISO PRIVADA, control positivo e invariantes.
3. Repite en contextos distintos: HUD, tutorial, diálogo, pantalla de controles, combate, ayudas. No extrapoles 0 hits ni 0 pixel diff de una pantalla a todos los lugares.
4. Si no se localiza recurso exacto, deja F2 abierta y documenta offsets, logs, evidencia y bloqueo concreto.

## Segunda tarea — QA completo de los diecinueve glifos españoles

Comprueba en **escenas auténticas de PPSSPP real**, mediante diálogos y textos que contengan `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`, las posiciones, ancho, recorte, mayúsculas, signos iniciales y combinaciones con símbolos. Si algún carácter no aparece naturalmente, construye **un texto de diagnóstico aislado**, sin editar el corpus canónico, conserva opcodes/eventos y restaura. Guarda **mínimo dos PNG reales por pantalla**, SHA-256 individual, versión, estado, métricas y comparación. No crees capturas artificiales ni llames aprobado a un carácter visto solo en un bitmap estático.

## Regresiones y verificación

Mantén `--event-safe-only`. F1 desde USA: 349 PSPFS, **345 recursos ajenos a cuatro contenedores textuales** idénticos, DSARC e ISO9660 ajenos, 51705 comandos, 46308 no textuales, 1625 scripts y cero offsets movidos. Las sondas FONT-only desde F1 preservan **348 recursos ajenos**. Cualquier BPS debe ser reaplicado contra su ISO de origen exacta y comparado SHA byte a byte. No distribuir ni subir ISO/BPS/assets. Proteger los 4524 scripts aplazados.

Comandos de regresión:
```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/reportar_integrabilidad_es.py --reporte /ruta/privada/f2-integrabilidad-nuevo.json
(cd patcher && go test ./...)
export ISO_ORIGINAL='/ruta/privada/Cladun_USA_original.iso'
export ISO_F1='/ruta/privada/f1-canonica-final.iso'
sha256sum "$ISO_ORIGINAL" "$ISO_F1"
python tools/auditar_atlas_f2.py --original "$ISO_ORIGINAL" --f1 "$ISO_F1" --salida /ruta/privada/f2-atlas-nuevo.json
python tools/generar_probe_f2_indice.py --f1 "$ISO_F1" --modo new --salida /ruta/privada/f2-new.iso --informe /ruta/privada/f2-new.json
python tools/generar_probe_f2_indice.py --f1 "$ISO_F1" --modo old --salida /ruta/privada/f2-old.iso --informe /ruta/privada/f2-old.json
```
Todos los destinos deben ser nuevos/inexistentes. Para compilar traducción desde USA utiliza los argumentos reales del integrador `--experimental-parcial --event-safe-only` y para BPS `--experimental --event-safe-only`; nunca quitar guardas. Ejecuta CI sobre el HEAD final y registra run IDs y resultados. No asumir cierre F2 por un éxito estático o CI.

## Fases y RELEVO RECURSIVO OBLIGATORIO

F2 sigue ABIERTA hasta identificar rutas gráficas y validar todos los glifos en pantalla. F3 introducción aún en inglés; F4 4524 traducciones SCRIPT pospuestas; F5 aventura/inventario/combate/guardar/cargar; F6 BPS final y EXE Windows probado integralmente. PR #7 debe permanecer en borrador.

**Al finalizar este trabajo actualiza `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, documentos de QA, hashes/capturas reales y PR, y REESCRIBE DE NUEVO `prompts/SIGUIENTE_TAREA.md` con un PROMPT COMPLETO Y AUTÓNOMO para el siguiente paso. MUESTRA ESE PROMPT EN EL CHAT. El nuevo prompt debe exigir explícitamente volver a generar otro al terminar, recursivamente hasta completar F2–F6.** 
