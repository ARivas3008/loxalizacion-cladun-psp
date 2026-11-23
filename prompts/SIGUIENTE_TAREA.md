# CLADUN ES — NUEVO RELEVO AUTÓNOMO F3-R2: IMY 0x02, ORIGEN DEL PRÓLOGO, 85 EVENTOS; F2 Y F4–F6 ABIERTAS

**Fecha:** 23/11/2026. **Mandato:** actúa como ingeniero sénior PSP MIPS, PPSSPP oficial 1.20.4, WebSocket/GE/VRAM, ISO9660/PSPFS/DSARC, IMY y CP932 español. REALIZA trabajo comprobable, pruebas y cambios de código solamente con causalidad; no te limites a aconsejar. Clasifica siempre evidencia (A) binarios originales auténticos, (B) sintético/CI y (C) PPSSPP real. No inventes imágenes, hashes, PCs, dumps, tests o éxitos.

## 0. OBLIGACIÓN RECURSIVA INNEGOCIABLE

**AL CONCLUIR, REESCRIBE COMPLETAMENTE prompts/SIGUIENTE_TAREA.md CON UN OTRO PROMPT NUEVO, ÍNTEGRO, AUTÓNOMO Y ACTUALIZADO**, incluyendo estado, archivos, hashes, comandos, resultados de CI, bloqueos y la **MISMA OBLIGACIÓN RECURSIVA** hasta que F2–F6 se completen REALMENTE. Muéstralo íntegro al usuario. Nunca prometas trabajo asíncrono o en segundo plano.

## 1. Contrato de GitHub y archivos obligatorios

- Repo https://github.com/ARivas3008/loxalizacion-cladun-psp
- Rama integracion-eventos-segura-20261120. PR #7 https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7 ; base revision-manual-dialogos.
- **Conservar PR ABIERTO, DRAFT, sin merge ni force push. No editar rama base ni corpus original.**
- Histórico inicial del usuario: HEAD 1fd924f0a5b06769b1a060f1778cd2f02621e628. Este relevo observó después HEAD b8118782f29c3ae273767f2499da2b778b421858 (2 commits adicionales). Son ANCESTROS: debes comprobar SHA ACTUAL y parent/tree al comenzar; nunca asumir esos SHA como actual.
- En el relevo anterior el terminal no resolvía DNS github.com, pero el conector GitHub sí funcionó. No fingir clonación. Si falta DNS, usar conector fetch_file, Git Data create_blob/create_tree/create_commit/update_ref con expected_sha real y force:false.

Comprobación de checkout real:

~~~bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
~~~

Leer ÍNTEGROS antes de tocar código: AGENTS.md, README.md, prompts/SIGUIENTE_TAREA.md, reports/ESTADO_CONTINUIDAD_PPSSPP.json, docs/F3_INTRO_INTENTO_PPSSPP_Y_ORIGEN_SCRIPTS_2026-11-23.md, docs/F3_PROLOGO_ANIME000_DEPENDENCIA_PPSSPP_REAL_2026-11-23.md, docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md, los reports F3 homónimos, tools/f3_auditar_intro.py, tools/f3_sonda_anime000_auditar.py, tools/f3_anime_imy_estructuras.py y todos sus tests. Conservar y leer las evidencias F2: docs/F2_WS_REAL_F1_CONTROLES_GE_2026-11-23.md, docs/F2_PPSSPP_REAL_X11_AB_TUIKA_2026-11-23.md, docs/F2_MAPA_JUGABLE_GE_X11_F1_2026-11-23.md, docs/RESULTADO_F1_PPSSPP_2026-11-21.md, los reportes respectivos y tools/f2_ws_procedencia_ppsspp.py, tools/f2_ppsspp_ws_1204.py, tools/f2_ge_dump_1204.py, tools/f2_tuika_proteger_subregiones.py. Para eventos leer tools/script_event_guard.py, tools/integrar_parche_seguro.py, tools/charset_es.py y tests de integración.

## 2. Binarios originales y SHA-256, SOLO PRIVADOS

- ISO USA original aportada por usuario: **305496064 B**, SHA256 **b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f**.
- ISO F1 canónica histórica: **306456576 B**, SHA256 **496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986**.
- BPS USA→F1 histórico: **daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd**.
- PPSSPP **oficial 1.20.4 AppImage Linux x86_64**: **50689748 B**, SHA256 **661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21**.
- URL oficial https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
- DATA.DAT original offset absoluto ISO **113770496**, longitud **191697408 B**, tabla PSPFS_V1 de **349** entradas.
- PSPFS 231 SCRIPT.SDT → SCRIPT.DAT SHA **c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358** y SCRIPT.TBL SHA **f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37**.
- PSPFS 234 ANIME000.IDT 3537936 B SHA **0e57353eb1d5f9688164b3453e57b0fd91ff77dee8e422844ba3fb0fef32eb37**.
- PSPFS 235 ANIME001.LDT 287472 B SHA **cb7f1354e38ced1a5b19f36c2b45d939e59094e33de901d4b43dc8d65faaa174**.
- PSPFS 236 ANIME002.LDT 2067856 B SHA **e1617dd4aea349f60953db9471e53c1524e9c3184b2566a4a732c3ecc756eec6**.

**PROHIBIDO subir ISO, DATA.DAT, BPS, PSP EBOOT, IMY/animaciones, fuentes del juego, recursos comerciales, PNG/capturas/vídeos de PPSSPP o dumps RAM/GE/VRAM.** Únicamente código, tests sintéticos, documentación, métricas e hashes públicos. A/B de ISOs y capturas **solo privados** y fuera de Git. No compartir assets originales, ni aunque no estén modificados.

## 3. Hallazgos nuevos de F3 — CONFIRMADOS A/B; NO identifican letras

Esta sesión extrajo la ISO original auténtica del 7z del usuario y la rehash verificó. Herramienta NUEVA tools/f3_anime_imy_estructuras.py, informe reports/RESULTADO_F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.json, documentación docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md y **14 tests sintéticos locales PASS**. No se ejecutó PPSSPP nuevamente en esta sesión, pues el AppImage no estaba disponible y el terminal carecía de DNS.

**A (original auténtico estático):**
- ANIME000.IDT: 231 cabeceras IMY literales estructuralmente consistentes: **136 tipo 0x00**, **95 tipo 0x02**.
- ANIME001.LDT: 24 cabeceras IMY de tipo 0x00.
- ANIME002.LDT: cero firmas IMY literales.
- En las 255 firmas, u32 de cabecera +4 = stride*rows + 32. Los primeros u32 de cada recurso son 192/24/39; NO atribuirlos sin prueba a cantidad de cuadros.
- El algoritmo de flags/lookbacks IMY legado consumió longitud correcta en **160/160 tipo 0x00**, pero falló **95/95 tipo 0x02** (55 lookback inválido, 40 longitud distinta). Es evidencia de **INCOMPATIBILIDAD DE FLUJO**, no un códec 0x02 resuelto; tipo 0x00 tampoco acredita paletas, geometría ni renderizado. No activar ni repintar tipo 0x02 mediante decodificador F2/SYSGRA 0xA4.
- Código e informes solo leen; no crean PNG, nuevas ISOs ni alteran traducciones.

Reproducción privada exacta:

~~~bash
sha256sum /PRIVADO/Cladun_USA.iso
python tools/f3_anime_imy_estructuras.py --iso-original /PRIVADO/Cladun_USA.iso --reporte /PRIVADO/ANIME_IMY_LECTURA_NUEVA.json
python -m unittest tests.test_f3_anime_imy_estructuras -v
~~~

**C histórico distinto:** en relevo previo PPSSPP 1.20.4 Vulkan real mostró el prólogo inglés. Sonda privada de 1 solo byte del descriptor PSPFS, offset ISO **113778009**, renombró ANIME000.IDT a ANIME000.XDT, produjo crash antes del título, PC PSP **0x08809498** leyendo **0x00000015**, y un A posterior recuperó el título original. ISO sonda privada SHA **576e9699395dd142b666ed3b9d121db5037c63302dc0c4eee862a04ccfcdbb36**. **SOLO prueba dependencia de arranque del nombre; NO procedencia de las letras. NO repetir renombrados destructivos para localizar imágenes.**

## 4. F3 PRIORIDAD 1: PRÓLOGO VISUAL EN INGLÉS

El prólogo antes del diálogo demo1001 muestra inglés tanto USA como F1. Frase real observada, ejemplo: “Some say, because the treasures were there.” No se encontró esa frase completa como ASCII literal en los 349 PSPFS descomprimidos. El match parcial en DATABASE.DAT/MONSTER.DAT fue un **falso positivo** (biografía de monstruo). La procedencia de la textura/letras sigue **NO DEMOSTRADA**.

Pasos, en orden:
1. Recuperar emulador oficial exacto SHA y USA original. Autenticar la MISMA sesión con PID/ISO FD/socket WS/versión, no solo log Booted.
2. Alcanzar el prólogo **REAL** sin alterar el archivo ANIME000. Registrar por WebSocket/PSP I/O recursos cargados, PC MIPS pertinente, RAM, GE gpu.record.dump con TEXADDR/CLUT/PRIM, y frames privados temporizados, durante una frase visible.
3. Comparar direcciones RAM y VRAM y datos de textura contra miembros PSPFS originales. Una coincidencia de nombre o un GE de otra pantalla NO acredita causalidad de texto.
4. Si no hay traza, investigar índices y formato 0x02 con parsers fail-closed y roundtrip; una hipótesis de frame/paleta requiere evidencia independiente. No inferir «delta» por un error de lookback.
5. Solo tras identificar textura/CLUT específica, preparar **sonda CROMÁTICA aislada, reversible y PRIVADA** que no afecte el arranque, certificar spans PSPFS/DSARC y demás recursos, y hacer A/B sincronizado + control negativo en la **misma escena**.
6. Solo cuando se demuestre procedencia, reconstruir letras españolas del prólogo en ROI limitado, sin tocar iconos/fondos/números, validar PSP 480x272, X11 960x544, tildes, paletas, rendimiento y una reproducción completa de la escena. Mantener evidencia comercial privada.

## 5. F3 PRIORIDAD 2: 85 DIÁLOGOS DEMO1001 BLOQUEADOS

Ruta: DATA.DAT → PSPFS 231 SCRIPT.SDT → DSARC SCRIPT.DAT/SCRIPT.TBL. Dos nombres: demo1001_00.dsf y demo1001_01.dsf; **7 bloques** ID 100000/100100/100190/100101/100191/100110/100120 con **878 comandos** por bloque **5/422/27/339/28/23/34**, 98 opcodes textuales y 97 cadenas no vacías. El borrador español tiene traducciones para las 97: 2728 bytes origen, 2859 CP932 español A1–B3; **85** distinta longitud, **11** longitud compatible candidatos, **1** sin cambio.

Estas 85 entradas NO se han integrado; mantener --event-safe-only. Para desbloquear:
1. Ejecutar tools/f3_auditar_intro.py sobre ISO original y CSV para verificar los 97 offsets/bytes/IDs 1:1.
2. Investigar intérprete PSP MIPS y estructura de saltos/llamadas a scripts; localizar destinos y referencias internas/externas de los comandos, no adivinarlo al encontrar un u16/u32 parecido a un offset.
3. Construir modelo de relocalización con pruebas independientes y fail-closed para 51705 comandos, 46308 comandos no textuales, 1625 bloques y metadatos SCRIPT.TBL. Si cambia longitud, verificar destino exacto de todos los saltos.
4. Solo con causalidad y tests, generar ISO privada de 85 cambios, auditar integridad completa y ejecutar demo1001 real USA/F1/candidato con diálogos, retratos, efectos, START SKIP y estados. Hasta entonces no autorizar reconstrucción variable.

## 6. Mantener F2 ABIERTA; F4–F6 sin falsear progreso

**F2 histórico C preservado**:
- PPSSPP oficial 1.20.4 ISO F1, Opciones 756 px interiores/≈764 exteriores, Sí/No, música y 6 iconos; WebSocket puerto 24192 version/game.status/cpu.status mismo PID+ISO; GE Controles 38546 B / 398 registros / 124 PRIM.
- Otra sesión PPSSPP F1 real alcanzó primer mapa jugable con HUD y movimiento tras START SKIP, backend OpenGL/llvmpipe Xvfb :98. GE 65309 B SHA **d2195fbedd6f430d2a3823db28c12f9f9a9bc789964adefead0bab19298f06b4**, 989 registros, 301 PRIM, 43 TEXADDR0, 40 CLUTADDR. NO demuestra TUIKA ni el prólogo.
- En prueba de splash SYSTEM PRiSM había 1152 píxeles magenta tanto USA como sonda: **0 diferencias**. NO atribuir magenta al TUIKA.
- F2 pendientes: A/B real TUIKA en combate/habilidad, traza MIPS→RAM→GE→VRAM, iconos en HUD/tutorial/combate y 19 glifos **áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō** en múltiples contextos. Mantener 2721 glifos originales, 19 A1–B3, white_new_ink=False por defecto.

**F4:** integrar con seguridad **4524** cambios de longitud de SCRIPT.DAT aplazados, solo con modelado y QA runtime. **F5:** juego completo, retratos, atlas, combate, enciclopedia, HUD, partidas guardadas/cargadas y regresión F1. **F6:** BPS final y EXE Windows x64 aplicados end-to-end y testados con ISO propia, sin distribuir payload. Conservar corpus 9237, traducción 9235/2 excepciones, 349 PSPFS, glosario, base y PR DRAFT.

### PPSSPP, solo cuando binarios se hayan revalidado

En antecedentes Vulkan/llvmpipe se usó Xvfb :88 **sin GLX**, SDL 960×544, SDL_AUDIODRIVER=dummy, SHARUN_ALLOW_LD_PRELOAD=1, INI cargado GraphicsBackend=3, VK_DRIVER_FILES y VK_ICD_FILENAMES apuntando a JSON absoluto privado de lavapipe. En otra sesión OpenGL/llvmpipe funcionó en Xvfb :98; no mezclar backends. Comandos orientativos después de validar ejecutable:

~~~bash
sha256sum /PRIVADO/Cladun_USA.iso /PRIVADO/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
Xvfb :88 -screen 0 1280x720x24 -ac -extension GLX +render -noreset &
export DISPLAY=:88 SDL_AUDIODRIVER=dummy SHARUN_ALLOW_LD_PRELOAD=1
export VK_DRIVER_FILES=/PRIVADO/lvp_absolute.json
export VK_ICD_FILENAMES=/PRIVADO/lvp_absolute.json
# Verificar el INI efectivamente cargado; arrancar AppImage oficial con argumentos reales.
~~~

## 7. Validación, PUBLICACIÓN SEGURA y RECURSIVIDAD

~~~bash
python -m unittest discover -s tests -v
python -m unittest tests.test_f3_auditar_intro tests.test_f3_sonda_anime000_auditar tests.test_f3_anime_imy_estructuras -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f3_preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f3_integrabilidad.json
(cd patcher && go test ./...)
git diff --check
git rev-parse HEAD
~~~

Si falta checkout, **NO atribuir esos comandos a ejecución local**: verificar GitHub Actions por separado. Publicar solo herramientas/tests sintéticos, JSON de métricas y docs, preservando todo F2 y el borrador. Commit fast-forward con expected_sha y force:false. Comprobar GitHub PR #7 todavía DRAFT y **dos validaciones de GitHub Actions (push y pull_request) sobre el mismo SHA HEAD FINAL** ambas SUCCESS; si no, registrar estado real sin suponer éxito.

Entregar: evidencia A/B/C diferenciada, código modificado, ruta, comandos, hash, tests locales y CI, hallazgos y bloqueos, estado F2–F6. **REESCRIBIR COMPLETAMENTE prompts/SIGUIENTE_TAREA.md COMO UN TERCER PROMPT NUEVO, AUTÓNOMO Y ACTUALIZADO CON ESTA MISMA OBLIGACIÓN RECURSIVA INNEGOCIABLE; MOSTRARLO ÍNTEGRO AL USUARIO AL TERMINAR.** Nada de promesas de entrega futura.
