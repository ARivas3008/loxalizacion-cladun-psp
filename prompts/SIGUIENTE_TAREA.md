# CLADUN ES — RELEVO AUTÓNOMO F3: 85 TEXTOS DE INTRODUCCIÓN BLOQUEADOS, PPSSPP OFICIAL Y F2/F4–F6

Actúa como especialista PSP MIPS, PPSSPP oficial v1.20.4 WebSocket, ISO9660/PSPFS/DSARC, SCRIPT.DAT y localización CP932 A1–B3. Trabaja DE VERDAD: lee ISO original, ejecuta tests, estudia referencias, programa correcciones si son seguras, actualiza GitHub y presenta evidencias. NUNCA inventes capturas, emulación, direcciones MIPS/RAM/VRAM, hashes o resultados. Separa siempre (A) bytes ISO originales, (B) pruebas sintéticas/CI y (C) ejecución real PPSSPP.

OBLIGACIÓN RECURSIVA HASTA F2–F6: AL CONCLUIR REESCRIBE COMPLETAMENTE prompts/SIGUIENTE_TAREA.md con OTRO PROMPT ÍNTEGRO, NUEVO, AUTÓNOMO Y ACTUALIZADO, que VUELVA a exigir la misma regeneración recursiva. MOSTRAR EL PROMPT COMPLETO al usuario. No prometas trabajo en segundo plano.

## 1. GitHub y estado

Repo https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama integracion-eventos-segura-20261120
PR https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7 — DRAFT, base revision-manual-dialogos, abierto, sin merge, sin force push.

HEAD anterior al relevo F3: 1e3acb99ec655de11026438a057eda8dcc96568d. GitHub Actions sobre ese HEAD: push 45177111153 y PR 45177122057, ambos SUCCESS, 475 tests Python (1 omitida), Go/integridad/compilación Windows pública sin payload. Este no será necesariamente el HEAD actual. Leer ref, tree, PR y DOS Actions del SHA final tras cualquier commit.

Leer COMPLETOS: AGENTS.md, README.md, prompts/SIGUIENTE_TAREA.md, reports/ESTADO_CONTINUIDAD_PPSSPP.json, docs/F3_INTRO_INTENTO_PPSSPP_Y_ORIGEN_SCRIPTS_2026-11-23.md, reports/RESULTADO_F3_INTRO_ORIGEN_2026-11-23.json, tools/f3_auditar_intro.py, tests/test_f3_auditar_intro.py; docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/RESULTADO_F1_PPSSPP_2026-11-21.md, docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md; tools/extract_cladun.py, tools/charset_es.py, tools/integrar_parche_seguro.py, tools/script_event_guard.py, tools/iso_guard_global.py, tools/generar_parche_bps.py; F2 tools y docs de 19 glifos, TUIKA, captura WS, testigo /proc y rastreo GE.

Si se dispone de checkout real:
    git fetch origin
    git switch integracion-eventos-segura-20261120
    git pull --ff-only
    git status --short
    git rev-parse HEAD
    git rev-parse HEAD^{tree}

En entornos pasados DNS github.com falló y no hubo clone; sí funcionó el conector GitHub mediante fetch refs, create_blob/create_tree/create_commit/update_ref con expected_sha, force:false. No fingir checkout local. Nunca subir ISO, BPS, EBOOT, DATA.DAT, recursos del juego, IMY/FONT, PNG, dumps RAM/GE/VRAM, grabaciones/capturas ni ejecutables comerciales.

## 2. PPSSPP: evidencia histórica auténtica, falta binario en entorno ACTUAL

PPSSPP SÍ se ejecutó realmente en el proyecto antes: versión oficial 1.20.4 Linux x86_64 AppImage, llvmpipe, Xvfb 1280x720, ventana X11 960x544, Cladun y prueba de Opciones (756 píxeles interior y aproximadamente 764 exterior). Está documentado en docs/RESULTADO_F1_PPSSPP_2026-11-21.md. No desacreditar F1 histórico solo porque ahora falte el binario.

AppImage oficial exacto:
https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
Release https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4
SHA256 histórico del AppImage: 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21
Tamaño del asset: 50689748 bytes.

En el entorno actual no se encontró AppImage ni PPSSPPSDL/PPSSPPQt; Xvfb sí disponible; curl a GitHub y descarga directa fallaron por DNS. Intentar instalar desde release OFICIAL o recuperar caché/otro entorno legítimo y validar SHA antes de ejecutar. No reemplazar PPSSPP por imagen sintética ni inventar gameplay.

    uname -m
    command -v Xvfb
    command -v PPSSPPSDL || command -v PPSSPPQt
    sha256sum /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
    Xvfb :99 -screen 0 1280x720x24 &
    export DISPLAY=:99
    export SDL_AUDIODRIVER=dummy

## 3. DESCUBRIMIENTO VERIFICADO EN F3: traducciones YA EXISTEN

La ISO USA auténtica aportada por el usuario tiene 305496064 bytes y SHA256:
    b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f

ISO F1 canónica histórica SHA 496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986
BPS canónico F1 histórico SHA daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd

Ruta origen narrativa: PSP_GAME/USRDIR/DATA.DAT → PSPFS índice 231 SCRIPT.SDT → DSARC SCRIPT.DAT y SCRIPT.TBL → demo1001_00.dsf / demo1001_01.dsf.
Original SCRIPT.DAT SHA c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358
Original SCRIPT.TBL SHA f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37

La ISO REAL contiene 7 bloques ID 100000/100100/100190/100101/100191/100110/100120, 878 comandos, 98 opcodes textuales incluyendo 1 vacío, 97 campos originales NO vacíos y 2728 bytes textuales. Script ID 100100 incluye 44 textos, ID 100101 45, ID 100110 5 e ID 100120 3. No hay archivos nombrados .PMF en ISO9660 o PSPFS, pero NO se descartan otros vídeos ni inglés de gráficos. No confundir nombres de archivos con gameplay probado.

El BORRADOR real de GitHub traduccion/CLADUN_BORRADOR_ES.csv, blob 400a9c9ec06f7456b5ec6e11f7502d711b0a976e, tiene 9237 filas. LAS 97 FILAS demo1001 YA ESTÁN TRADUCIDAS al español. Su codificación exacta A1–B3 y CP932 ㊦/㊧/㈱ suma 2859 bytes.
- ID 100100: 38 de distinta longitud, 5 igual longitud y 1 sin cambio.
- ID 100101: 40 de distinta longitud, 5 igual longitud.
- ID 100110: 4 distinta longitud, 1 igual longitud.
- ID 100120: 3 distinta longitud.
TOTAL 85 CAMBIOS DE LONGITUD PROTEGIDOS +11 COMPATIBLES EN LONGITUD +1 IDÉNTICO.

El inglés persiste potencialmente PORQUE --event-safe-only bloquea 85 diálogos traducidos cuya inserción desplazaría instrucciones o referencias no demostradas. Estos 85 pertenecen a los 4524 cambios SCRIPT.DAT aún aplazados. No cortar traducciones ni desactivar guardia; 11 de igual longitud son solo candidatos, NO evidencia visual F1.

## 4. PRIORIDAD F3: reparar sin romper el intérprete de eventos

Ejecutar contra ISO original y CSV reales la herramienta NUEVA de solo lectura tools/f3_auditar_intro.py que coteja 97 textos uno a uno por offset_hex, bytes_hex, script_id, nombre, longitud, original y codificación:

    python tools/f3_auditar_intro.py \
      --iso-usa /PRIVATE/USA_original.iso \
      --borrador-es traduccion/CLADUN_BORRADOR_ES.csv \
      --reporte-privado /PRIVATE/F3_AUDITORIA_NUEVA.json

Si no hay CSV auténtico accesible, omitir --borrador-es y declarar evaluación de traducciones NO realizada en esa ejecución. Guardar reporte nuevo FUERA del checkout, sin sobrescrituras. Ejecutar tests/test_f3_auditar_intro.py (sintéticos) y contrastar todos los bytes de fuente.

Luego investigar llamadas/destinos de salto, offsets y referencias cruzadas desde SCRIPT.TBL y programa MIPS, para proponer una reubicación segura de **solo los 85 textos**. Crear un prototipo sintético y una guarda binaria independiente antes de parchear. Conservar semántica/orden de 51705 comandos, 46308 no textuales, 1625 comienzos, 349 PSPFS y recursos no textuales. Que los opcodes coincidan NO basta si saltos/punteros cambian. Si la seguridad no se demuestra, conservar los 85 bloqueados.

Si PPSSPP real vuelve a estar disponible, reconstruir ISO F1 de control con SHA exacto, crear candidato privado SOLO si supera guardas, ejecutar intro completa con controles original/parche, confirmar español en PPSSPP y capturas X11 o depurador reales, sin imágenes fabricadas. Verificar cuadros, retratos, fuentes, acentos, animaciones, estabilidad y retornos. No declarar F3 terminada sin QA runtime.

## 5. F2 pendiente y siguientes F4–F6

El usuario ordena AVANZAR F3 sin esperar F2. F2 sigue ABIERTA: validar 19 glifos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō, dos fuentes, iconos, TUIKA y cadena MIPS→RAM→GE→VRAM, más regresión X11 de F1. Mantener white_new_ink=False y los 2721 glifos originales.

F4: resolver 4524 cambios SCRIPT.DAT de distinta longitud con saltos/referencias verificables.
F5: QA integral de historia, combate, HUD, opciones, inventario, retratos, diálogos, guardado/carga.
F6: BPS español final SHA/source/target y parcheador EXE Windows probado end-to-end. No liberar ISO ni assets comerciales, ni declarar 100%, ni fusionar PR #7.

Las operaciones parciales siguen estrictamente --event-safe-only; BPS experimental --experimental --event-safe-only. Todos los gráficos y archivos ajenos a texto quedan intactos.

## 6. Pruebas, publicación y RECURSIVIDAD

En checkout real:
    python -m unittest discover -s tests -v
    python -m unittest tests.test_f3_auditar_intro -v
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/f3-preflight.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/f3-integrabilidad.json
    (cd patcher && go test ./...)
    git diff --check

Sin checkout verdadero, inspeccionar DOS GitHub Actions sobre el SHA final, Python/Go/integridad/build Windows público SIN payload. No atribuir CI a gameplay. Antes de finalizar (1) ejecutar tareas reales, separar evidencias y bloqueos, (2) actualizar docs/reports/ESTADO_CONTINUIDAD_PPSSPP.json, (3) commit seguro rama con expected_sha y force:false, PR #7 DRAFT sin merge, (4) comprobar dos CI SUCCESS del MISMO HEAD FINAL, (5) REESCRIBIR COMPLETAMENTE prompts/SIGUIENTE_TAREA.md con NUEVO PROMPT AUTÓNOMO que EXIJA LA MISMA OBLIGACIÓN RECURSIVA y MOSTRARLO ÍNTEGRO. Repetir hasta F2–F6 realmente completadas.
