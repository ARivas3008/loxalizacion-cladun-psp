# CLADUN ES — NUEVO RELEVO AUTÓNOMO F2/F3-R7: 11 DIÁLOGOS DE IGUAL TAMAÑO SIMULADOS, 85 EVENTOS BLOQUEADOS, PPSSPP TUIKA Y 19 GLIFOS; F4–F6 ABIERTAS

**Corte: 23/11/2026.** Eres ingeniero sénior PSP MIPS, PPSSPP oficial 1.20.4, WebSocket/GE/VRAM, ISO9660/PSPFS/DSARC, IMY, CLUT y localización CP932 española. **EJECUTA** trabajo comprobable, tests y correcciones solamente con causalidad. NO basta aconsejar. Divide las evidencias: **A original ISO comercial auténtica**, **B datos reales de borrador y tests sintéticos/CI**, **C ejecución auténtica de PPSSPP**. Nunca inventes PC MIPS, dumps, capturas, hash, disponibilidad, Actions ni publicaciones.

## 0. REGENERACIÓN RECURSIVA INNEGOCIABLE

**AL CONCLUIR REEMPLAZA ÍNTEGRAMENTE `prompts/SIGUIENTE_TAREA.md` POR OTRO PROMPT NUEVO, COMPLETO, AUTÓNOMO Y ACTUALIZADO CON HEAD, ESTADO PR, DATOS/HASHES, RESULTADOS A/B/C, ARCHIVOS, COMANDOS, BLOQUEOS Y CI. MUÉSTRALO ÍNTEGRO AL USUARIO. EL PROMPT NUEVO EXIGIRÁ LA MISMA REGENERACIÓN RECURSIVA, EN CADA RELEVO HASTA CERRAR REALMENTE F2–F6.** Si falta una prueba, registrar el bloqueo; no prometer trabajo asíncrono.

## 1. Repo, estado y lecturas

Repo: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: `integracion-eventos-segura-20261120`
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base: `revision-manual-dialogos`.
**Conservar OPEN/DRAFT, sin merge, sin force push, sin editar rama base ni corpus fuente.**

HEAD auténtico al inicio de este relevo F3-R6: `a3b7f8c5b663b86b070c8af06378faf1e250fea6` (NO asumir HEAD actual al siguiente turno). HEAD histórico F3-R5 de pruebas: `e0e47fa0e145732c83769af22c3a57e3fcc8eb4c` (CI push y PR SUCCESS). Ancestros F3-R4: `0c4a606c397d00e176bed4b11f62833d44803e0d`, F2 paralelo A/B/A: `161b7d4f2f64656f67143f8cbdd9e3290dd691ea`. **NINGUNO DE ELLOS DEBE SUPONERSE HEAD ACTUAL.** Comprobar inmediatamente:

~~~bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
~~~

Si terminal falla por DNS github.com, no fingir checkout; usar GitHub conector `fetch_file`, `create_blob/create_tree/create_commit/update_ref` con `expected_sha` y `force:false`, comprobando la rama antes de escribir y conservando trabajos paralelos F2.

LEER COMPLETOS: `AGENTS.md`, `README.md`, `prompts/SIGUIENTE_TAREA.md`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/F3_R6_SIMULACION_11_MISMA_LONGITUD_2026-11-23.md`, `reports/RESULTADO_F3_R6_SIMULACION_11_2026-11-23.json`, `tools/f3_simular_intro_mismo_tamano.py`, `tests/test_f3_simular_intro_mismo_tamano.py`, `tools/f3_presupuesto_padding_intro.py`, `reports/F3_DEMO1001_PADDING_ORIGINAL_2026-11-23.json`, `docs/F3_R5_ANCLA_DEMO1001_Y_DERIVA_2026-11-23.md`, `reports/RESULTADO_F3_R5_ANCLA_Y_DERIVA_2026-11-23.json`, `reports/F3_DEMO1001_GEOMETRIA_ORIGINAL_2026-11-23.json`, `tools/f3_anclar_intro.py`, `tests/test_f3_anclar_intro.py`, `tools/f3_auditar_intro.py`, `tools/f3_campos_alineacion.py`, `tools/f3_referencias_riesgo.py`, `tools/script_event_guard.py`, `tools/integrar_parche_seguro.py`, `tools/charset_es.py`, `docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md`, `docs/F3_ANIME_TOPOLOGIA_2026-11-23.md`, `docs/F3_PROLOGO_ANIME000_DEPENDENCIA_PPSSPP_REAL_2026-11-23.md`. Para F2: `docs/F2_COTEJO_X11_ABA_CONTROL_TEMPORAL_2026-11-23.md`, `docs/F2_IMPACTO_GLOBAL_CLUT2_REAL_2026-11-23.md`, `docs/F2_GE_ONLY_WEB_SOCKET_SIN_FRAMEBUFFER_2026-11-23.md`, `docs/F2_MAPA_JUGABLE_GE_X11_F1_2026-11-23.md`, `tools/f2_cotejar_x11_aba.py`, `tools/f2_ppsspp_ws_1204.py`, `tools/f2_ruta_ws_liberacion_segura.py`, `tools/f2_ws_procedencia_ppsspp.py`, `tools/f2_ge_dump_1204.py` y sus tests.

## 2. ISO y PPSSPP: binarios solamente PRIVADOS

- ISO USA original aportada del 7z, **305496064 bytes**, SHA256 **b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f**. No modificar.
- ISO F1 canónica histórica **306456576 bytes**, SHA256 `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`. BPS histórico USA→F1 SHA `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`.
- PPSSPP oficial 1.20.4 AppImage Linux x86_64: **50689748 bytes**, SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`, URL https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage.
- DATA.DAT ISO offset **113770496**; PSPFS **349**. PSPFS 231 SCRIPT.SDT → SCRIPT.DAT SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, SCRIPT.TBL SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`.

**PROHIBIDO subir o compartir ISO, BPS, EBOOT, DATA.DAT, IMY/FONT comerciales, sprites, vídeos, PNG de PPSSPP, RAM, GE, VRAM y dumps a GitHub o entregables públicos.** Solo código propio, tests sintéticos, metadatos agregados e hashes, y docs. Toda sonda ISO, capturas y A/B fuera del checkout, en privado. El AppImage faltó en F3-R5 y las descargas fallaron: NO hubo nueva ejecución PPSSPP C.

## 3. NUEVO F3-R5: ISO original → borrador español anclados sin ISO en CI

En **A** se extrajeron realmente de ISO original los 97 campos no vacíos de siete bloques `demo1001_00/01`, 878 comandos dentro de 1.625 bloques/51.705 comandos globales. Las 97 cadenas suman 2.728 bytes CP932 origen. Se computó una huella SHA256 de dominio separado de **offset + ID script + bloque + ordinal de comando + longitud + bytes originales**:

`b0d42d8cd871246addf08a54e02c2a84cda52cab39f5810ef5ba2d9173e3e34e`

Se conservó un manifiesto público **SOLO METADATOS** (`reports/F3_DEMO1001_GEOMETRIA_ORIGINAL_2026-11-23.json`, 97 posiciones, siete bloques, sin strings originales), verificado contra ISO original privada.

En **B**, `tools/f3_anclar_intro.py` y `tests/test_f3_anclar_intro.py` comprobaron contra el CSV REAL `traduccion/CLADUN_BORRADOR_ES.csv` (Git blob SHA1 `400a9c9ec06f7456b5ec6e11f7502d711b0a976e`) las **9.237 filas**, las 97 correspondencias individuales de offsets/script/original/bytes, la huella anterior y las 97 cadenas españolas codificadas A1–B3. **85** traducciones distintas longitudes bloqueadas, **11** mismo tamaño candidatas, **1** sin cambio; 2.859 bytes ES, +131 frente a origen. Pruebas locales: **14 sintéticas PASS**; en GitHub Actions **676 pruebas Python** PASS sobre código REAL, incluido un test de anclaje con CSV de 3,9 MB. Actions en HEAD histórico `e0e47fa0e145732c83769af22c3a57e3fcc8eb4c`: push run **45253114057** SUCCESS; pull_request run **45253129304** SUCCESS. No atribuirles emulación C.

**Resultado de riesgo NUEVO:** en una concatenación LINEAL hipotética de los 85 textos, manteniendo orden, **588 de 878 inicios de comando cambiarían dentro de sus bloques**, variación neta **+131 bytes**:
- Script 100000: delta 0 / desplazados 0.
- Script 100100: delta −1 / desplazados **268**.
- Script 100190: delta 0 / desplazados 0.
- Script 100101: delta +115 / desplazados **298**.
- Script 100191: delta 0 / desplazados 0.
- Script 100110: delta +15 / desplazados **10**.
- Script 100120: delta +2 / desplazados **12**.

**588 NO son saltos rotos, 588 punteros ni 588 PCs MIPS reales**: proyección sin padding, alineación, intérprete ni referencias externas; NO se reconstruyó SCRIPT.DAT, NO se autorizan los 85. Conservar `--event-safe-only`.

Comandos de reproducción:
~~~bash
# CI con borrador real, sin ISO comercial
python tools/f3_anclar_intro.py
python -m unittest discover -s tests -p 'test_f3_anclar_intro.py' -v

# Solo con ISO propia PRIVADA autenticada y salida NUEVA fuera de Git:
python tools/f3_anclar_intro.py --borrador-es traduccion/CLADUN_BORRADOR_ES.csv --geometria reports/F3_DEMO1001_GEOMETRIA_ORIGINAL_2026-11-23.json --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/ANCLA_R6_NUEVO.json
~~~

## 4. F3 prioridades: MIPS REAL, 85 eventos y prólogo gráfico

1. Recuperar PPSSPP 1.20.4 oficial de hash exacto, con ISO original. Autenticar **MISMA** sesión PID/starttime + FD ISO + WebSocket 24192 socket del mismo PID + version/game.status/cpu.status. Llegar a `demo1001` real.
2. Observar intérprete MIPS en ejecución: PCs, lecturas de SCRIPT.DAT, opcodes auténticos 0x02/0x0A y cualquier control de flujo. Inspeccionar código descifrado de la propia RAM si fuera posible, **solo privado**, jamás compartir dump. Verificar semántica y destinos efectivos de saltos antes de modelar reubicación.
3. Auditar 97 offsets/IDs frente al CSV con la nueva huella y `tools/f3_auditar_intro.py`. Construir modelo fail-closed para 1.625 scripts/51.705 comandos y TODAS referencias internas/externas. No cambiar longitudes de 85 hasta MIPS y regresión PPSSPP de demo1001 con diálogos, START SKIP, retratos y estados.
4. Prólogo visual sigue INGLÉS y de origen no demostrado. Frase observada «Some say, because the treasures were there.». ANIME000.IDT 231 firmas IMY (136 tipo00, 95 tipo02); el decodificador legado falla en tipo02. Sonda antigua renombró ANIME000 y provocó crash PRE-TÍTULO, no prueba fuente de letras; NO repetir. Registrar durante frase real I/O→RAM→GE gpu.record.dump TEXADDR/CLUT/PRIM→VRAM y textura CLUT; solo tras causalidad preparar sonda cromática reversible privada + A/B control negativo, ROI PSP 480×272 / X11 960×544.
5. El EBOOT.BIN original comienza por `~PSP` cifrado, no ELF MIPS llano; BOOT.BIN son ceros. No declarar intérprete desensamblado cuando no se ha extraído; necesitar PPSSPP real. Las 4.524 sustituciones globales de SCRIPT.DAT de distinta longitud siguen bloqueadas F4.

## 5. F2 paralelo y F4–F6: no perder ni falsear

F1 Opciones históricas en PPSSPP real: **756 px interior / ≈764 exterior**, Sí/No y seis iconos en Controles; otro C histórico alcanzó primer mapa jugable, GE 65.309 bytes/989 registros/301 PRIM. No implica F2 terminada.

F2 **ABIERTA**. Atlas TUIKA CLUT2 original auténtico: 256×256, índice2 **9.144 texeles** y **3.506 en siete zonas protegidas**; no cambiar paleta global para parche final porque recolorearía iconos, cifras, japonés. Sonda RGB de tres bytes solo diagnóstica. Ya existe `tools/f2_cotejar_x11_aba.py` de tres capturas independientes **USA antes → sonda → USA después** (16 tests sintéticos históricos), con control de píxeles inestables; usar junto a comparador A/B, X11 960×544 y `--ge-only` auténtico, nunca llamar X11 framebuffer WS. Sigue faltando **escena de combate/habilidad verdadera** en USA/sonda, vínculo causal TUIKA → RAM → MIPS → GE → VRAM, iconos HUD/tutorial y QA completo de 19 caracteres **áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō** en menús, ayudas, HUD y combate con distintas tintas. Mantener 2.721 glifos originales, 19 A1–B3 y `white_new_ink=False`.

F4: **4.524** textos script de diferente longitud aplazados. F5: QA integral juego ciudad/pisos/mapas/combat/habilidades/HUD/inventario/retratos/audio/guardado/carga/enciclopedia y regresión F1. F6: BPS final y EXE Windows x64 aplicados end-to-end y auditados con ISO propia en privado antes de distribución de parche, nunca payload comercial. Conservar 9.237 registros, 9.235 español/2 excepciones, 349 PSPFS, glosario, rama base y PR DRAFT.

## 5A. NUEVO F3-R6: 11 CAMBIOS DE IGUAL LONGITUD PROBADOS SOBRE ISO ORIGINAL EN MEMORIA

Se ejecutó realmente A **en ISO USA original auténtica privada**. Primero se autenticó tamaño 305496064 y SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`; se extrajo en memoria DATA.DAT→PSPFS 231 SCRIPT.SDT (IMY comprimido 8 bloques)→DSARC SCRIPT.DAT 633344B (SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`) y SCRIPT.TBL 52016B (SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`). Se verificaron 1625 bloques, 51705 comandos, 46308 no textuales, 7 bloques demo1001/878 comandos/97 textos/2728 bytes fuente.

Del CSV GitHub auténtico `traduccion/CLADUN_BORRADOR_ES.csv`, blob Git SHA1 `400a9c9ec06f7456b5ec6e11f7502d711b0a976e`, se seleccionaron SOLO LAS 11 traducciones de tamaño idéntico tras codificar CP932 español A1–B3. Se comprobó cada offset/texto fuente original/ID script y se sustituyeron los bytes en una copia PYTHON EN MEMORIA de SCRIPT.DAT, NUNCA en ISO ni BPS, sin exportar SCRIPT.DAT. Se realizó segunda lectura real integral: **51705/51705 comandos** mantuvieron inicio, ID, opcode y orden; **46308 no textuales** idénticos byte a byte; SCRIPT.TBL/inicios de los 1625 bloques sin cambios, 0 movimientos. Exactamente **11 campos** de texto se alteraron (211 bytes de contenido diferentes) en bloques 758,760,762; los otros 86 intro intactos. SHA256 virtual de archivo SOLO EN MEMORIA `f042e862cb0f47f4a172ab28872fe9d412d4b0c5f5cf6041b162a39e5531eee9`. **NO SE ESCRIBIÓ NI PUBLICÓ EL ARCHIVO**, y este dato estático NO prueba seguridad del intérprete MIPS o visual PPSSPP. Los 85 de longitud distinta siguen BLOQUEADOS.

Código B NUEVO: `tools/f3_simular_intro_mismo_tamano.py`, `tests/test_f3_simular_intro_mismo_tamano.py` (15 pruebas sintéticas y una integración con CSV real planeadas). Reutiliza el ancla ISO+CSV de `f3_anclar_intro`, el parser `read_commands` y `audit_script_rebuild(require_fixed_offsets=True)`, fuerza inmutabilidad de todos los comandos no textuales y tablas. Los tests CI deben ejecutarse con los scripts de repositorio reales, sin ISO. Los reportes públicos solo incluyen números, SHA y métricas; ninguna cadena/archivo comercial. Verificar GitHub Actions push y pull_request SUCCESS exactamente sobre HEAD final; no confundir B con juego C.

Comandos:

~~~bash
# CI / checkout sin ISO, valida SHA borrador real 9237 filas, huella 97 y 11 candidatas:
python tools/f3_simular_intro_mismo_tamano.py
python -m unittest discover -s tests -p 'test_f3_simular_intro_mismo_tamano.py' -v

# En contenedor local con ISO ORIGINAL del usuario y ruta privada, solo lectura + sim RAM:
python tools/f3_simular_intro_mismo_tamano.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/F3_R6_11_MISMO_TAMANO.json
~~~

**OTRO AVANCE PARALelo F3**: se añadió el test/plan de presupuesto de padding `tools/f3_presupuesto_padding_intro.py`, `tests/test_f3_presupuesto_padding_intro.py`, `reports/F3_DEMO1001_PADDING_ORIGINAL_2026-11-23.json`. Deben preservarse. Aunque un texto variable cupiera en tail padding, NO puede desplazarse comando ni saltar sin intérprete MIPS probado. Los **588 offsets hipotéticos desplazados**, 85 textos de longitud variable y 4524 globales siguen sin autorización de inserción. NO fusionar, NO forzar push, NO tocar rama base.

**C F2/F3 pendiente**: PPSSPP oficial 1.20.4 AppImage no existe en este contenedor; curl github.com falló por DNS y descarga alternativa falló. NO hubo nuevo juego, capturas, GE/VRAM/PC MIPS ni 19 glifos multicontesto. Prioridad adquirir binario auténtico SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`; A/B/A de TUIKA en combate usando USA/sonda, WS --ge-only con provenance y glifos 19 en ayudas/menús/combate. CLUT2 global afectaría 9144 texeles, 3506 protegidos: diagnóstico únicamente.

## 6. Publicación segura, CI FINAL y regeneración

Con checkout GIT real, y SOLO allí:
~~~bash
python -m unittest discover -s tests -v
python tools/f3_anclar_intro.py
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/preflight_f3_r6.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad_f3_r6.json
(cd patcher && go test ./...)
git diff --check
git rev-parse HEAD
~~~

No fingir estos comandos locales si solo se usa GitHub conector. Actualiza docs, reports y `reports/ESTADO_CONTINUIDAD_PPSSPP.json` preservando F2 paralelo; solo métricas/hashes/algoritmos, no assets. Commit fast-forward `expected_sha`, `force:false`. Confirmar PR #7 OPEN/DRAFT y DOS Github Actions **push/pull_request SUCCESS sobre el mismo HEAD FINAL**; si pendiente/fallo indicar estado auténtico y corregir si hay evidencia.

**REGENERACIÓN RECURSIVA INNEGOCIABLE: AL TERMINAR REESCRIBE COMPLETAMENTE ESTE PROMPT COMO OTRO NUEVO, AUTÓNOMO E ÍNTEGRO, MUESTRA TODO SU TEXTO AL USUARIO Y EXIGE QUE EL SIGUIENTE RELEVO LO VUELVA A REGENERAR HASTA COMPLETAR F2–F6 REALMENTE.**
