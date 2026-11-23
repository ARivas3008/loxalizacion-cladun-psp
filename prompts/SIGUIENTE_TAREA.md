# CLADUN ES — RELEVO AUTÓNOMO F4/F3-R10: TRÁFICO REAL DE 0x0A 100100 Y ORIGEN DEL PRÓLOGO; T/G/R/Q ABIERTAS

Fecha de corte: 23/11/2026. Repositorio https://github.com/ARivas3008/loxalizacion-cladun-psp; rama integracion-eventos-segura-20261120, base revision-manual-dialogos y PR #7 OPEN/DRAFT. HEAD verificable antes del commit documental R9: 18ff23f3f73e5a5537f2fc912f202239aba8a19b; este relevo R10 se publicó DESPUÉS, por lo que DEBES consultar git rev-parse HEAD o GitHub API, anotar SHA EFECTIVO, estado CI push/PR y cambios concurrentes antes de escribir. Sin force push, sin merge ni modificación de la rama base.

Actúa como ingeniero sénior PSP MIPS y PPSSPP oficial v1.20.4, ISO9660/PSPFS/DSARC, gráficos IMY/CLUT CP932 español, QA y localización. Ejecuta realmente código, análisis, tests y correcciones basadas en causalidad. Separa A=ISO original comercial auténtica privada, B=código/CI/sintéticos, C=gameplay auténtico con emulador y procedencia de proceso. NO inventes saltos, PCs, GPU, capturas, hashes, pruebas, publicaciones ni éxito.

## 0. REGLA RECURSIVA INNEGOCIABLE (reproducir completa en siguiente relevo)

**Si cualquiera de los cuatro apartados sigue por debajo del 100 % VERIFICADO, al terminar CADA relevo debes sustituir por completo prompts/SIGUIENTE_TAREA.md en la rama de trabajo mediante un NUEVO prompt autosuficiente y exigirle que haga lo mismo al acabar.** No copies sin actualizar el prompt anterior. Incluye HEAD real, PR y CI reales, estado de cuatro áreas, pruebas A/B/C, hashes reales, archivos concretos, comandos correctos, fallos, hipótesis, tareas no terminadas, próximos criterios de cierre y prohibiciones. Muéstralo íntegro al usuario. Continúa por relevos en nuevas sesiones **solo mientras** existan tareas pendientes; cuando estén **las cuatro al 100 % confirmado**, cambia el entregable a informe final, checklist de lanzamiento y prompt de mantenimiento pospublicación. No generes artificialmente otro relevo de desarrollo tras cierre completo. Si no tienes acceso a GitHub, entrega el archivo nuevo en el chat y marca la escritura remota como NO EJECUTADA.

Si se bloquea PPSSPP, haz máxima auditoría segura en sesión y deja bloqueo+condición precisa de desbloqueo. Una prueba B nunca sustituye C. No prometas trabajo en segundo plano.

## 1. Estado y evidencias a no falsear

TRADUCCIÓN T: 9.235/9.237 registros escritos (99,98% de borrador, NO de calidad/en juego); textos de origen truncado 008723/008724 y los gráficos del prólogo siguen sin validarse. Inventario total visible, revisión contextual y aprobación en ejecución NO MEDIBLES.
GRÁFICOS G: 6 PNG en SYS.DAT2 y 27 IMY SYSGRA analizados históricamente, total gráfico visible NO MEDIBLE. TUIKA_MES.IMY tiene 9.144 texeles de CLUT2 y 3.506 en subregiones protegidas; NO realizar recolor global; falta A/B/A en combate real y 19 glifos multicontesto.
ROMHACKING R: 3.724/8.248 cambios binarios planificados aplicados solo en candidata histórica (45,15% del conjunto); 4.524 diferidos por --event-safe-only. demo1001: 97 textos, 11 mismo tamaño simulados RAM-only, 85 variables bloqueados y 1 idéntico; 588 inicios cambiarían en hipótesis lineal, padding 48B y capacidad extra mínima 144B en tres bloques. Sin MIPS real y sin BPS+EXE final.
BETATESTING Q: matriz inicial ampliada de 42 a 43 casos, con nuevo Q043 de la hipótesis 0x0A; los 43 están NOT_RUN en este relevo (no se convierte historial F1 en PASS de la candidata final). Universo total de escenarios NO MEDIBLE.

EVIDENCIA A R9 AUTÉNTICA: ISO USA original extraída privadamente del archivo 7z del usuario, 305496064 bytes SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. DATA.DAT PSPFS 349; SCRIPT.DAT 633344B SHA256 c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358; SCRIPT.TBL 52016B SHA256 f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37. En A se reparsearon 1.625 scripts/51.705 comandos/46.308 no textuales, 7 bloques demo1001/878 comandos. La ISO permanece intacta. No asumir que la ruta temporal sobreviva al siguiente turno.

HALLAZGO F4 R9: 0x0A tiene 862 comandos con argumentos u32 de 4B; 320/862 valores coinciden con IDs de SCRIPT.TBL, 183 IDs distintos. Coincidencia externa singular: scr01.dsf, script ID 69, bloque 20, orden 20, comando offset 7420 de SCRIPT.DAT, opcode 0x0A, instruction_id 818, argumento 100100; hay un script ID 100100 en bloque 758, demo1001_00.dsf, inicio 218128. Es correspondencia ESTÁTICA, no una llamada probada. El opcode 0x01 usa payload 4B (4061 comandos), 0x02 usa payload 18B (2039 comandos). Los 21 matches relativos anteriores son SOLO SEIS PATRONES reiterados, muchos de valores frecuentes 23/32/55/85. 0x02 en campo+2 toma valor 23 en 1714/2039 instancias y en +6 toma 32 en 1439/2039: coincidencias a comandos internos podrían ser accidentales. Cero saltos probados.

B R9: tools/f4_r9_perfil_opcodes.py con tests/test_f4_r9_perfil_opcodes.py: 13 tests sintéticos PASS locales. La función profile pasó contra comandos autenticados mediante parser ISO independiente. Informe privado sin bytes comerciales SHA256 590db156de24d894a3109369278733296d9074f59eae52aa903b828ae0dc0bc9; ver reporte público reports/F4_R9_PERFIL_OPCODES_2026-11-23.json, docs/F4_R9_PERFIL_OPCODES_2026-11-23.md. GitHub CI sobre HEAD final debe verificarse, sin presumir PASS futuro.
C R9: PPSSPP oficial 1.20.4 NO EJECUTADO porque no está instalado y GitHub DNS del terminal no resuelve; capturas F1 y primer mapa son históricas, no actuales.

## 2. Primer paso, código y comandos

Leer completos AGENTS.md, README.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md, docs/F4_R9_PERFIL_OPCODES_2026-11-23.md, reports/F4_R9_PERFIL_OPCODES_2026-11-23.json, tools/f4_r9_perfil_opcodes.py, tools/f4_referencias_demo1001.py, tools/f3_referencias_riesgo.py, tools/script_event_guard.py, tools/f3_anclar_intro.py, tools/f3_simular_intro_mismo_tamano.py, tools/f3_presupuesto_padding_intro.py, docs/F3_R6_PADDING_ORIGINAL_Y_CAPACIDAD_2026-11-23.md, docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md, docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md, reports/ESTADO_CONTINUIDAD_PPSSPP.json, reports/COBERTURA_4_AREAS.json, qa/MATRIZ_BETATESTING_COBERTURA.csv, docs/ESTADO_CIERRE_4_AREAS.md y este prompt. Mantener 19 glifos A1–B3, white_new_ink=False; no regresar a F5A0–F5B2.

Si hay checkout auténtico, no reclonar encima:

    git fetch origin
    git switch integracion-eventos-segura-20261120
    git pull --ff-only
    git rev-parse HEAD
    git status --short
    python -m unittest discover -s tests -v
    python -m unittest discover -s tests -p 'test_f4_r9_perfil_opcodes.py' -v
    python tools/qa_cobertura_4_areas.py
    python tools/qa_cobertura_4_areas.py --require-closed  # DEBE FALLAR TODAVÍA
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
    (cd patcher && go test ./...)
    git diff --check

Con ISO original auténtica en directorio PRIVADO, fuera del checkout y usando ruta nueva:

    python tools/f4_r9_perfil_opcodes.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F4_R10_PERFIL_NUEVO.json

No ejecutar flags supuestos de otras herramientas: leer --help.

## 3. P0 concreto: probar o descartar 0x0A/100100 CON MIPS REAL

Conseguir PPSSPP 1.20.4 oficial autenticado, SHA256 histórico AppImage 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21; documentar backend, PID, starttime, FD a ISO original de hash correcto y WebSocket 24192 en el MISMO proceso. Reproducir escena donde scr01.dsf realmente se ejecute; no asumir que arranca automáticamente.

En depurador, localizar estructura en RAM que representa SCRIPT.DAT offset 7420 (NO asumir RAM addr=offset), identificar cuándo el intérprete consume opcode 0x0A/ID 818/u32 100100; registrar PCs MIPS reales, registros, origen, acción de despacho, cambio de script y retorno. Comparar secuencia original con control positivo que demuestre qué campo dirige la ejecución, usando sondas privadas acotadas y reversible SOLO si no rompen el arranque. Registrar evidencia C y descartar hipótesis si no hay lectura ni transferencia. Extender modelo a llamadas/scripts indirectos y textos variables antes de cualquier relocalización.

Para 0x01/0x02 NO repetir 21 falsos punteros como supuestos saltos: comprobar primero significado de sus valores frecuentes 23/32/55/85 en diversas escenas, analizar controles, tamaños y semántica de argumentos. La correspondencia con offsets de comandos puede ser coincidencia. Cubrir además ordinales, referencias de 16 bits, SCRIPT.TBL y otros callsites antes de liberar los 85 cambios variables demo1001 o 4524 globales.

## 4. P0 F3 y P1 T/G/Q + F6

F3: frase inglesa real Some say, because the treasures were there. procedencia gráfica no comprobada. ANIME000.IDT posee 231 firmas IMY (136 tipo00,95 tipo02) pero no demuestra autoría de letras; sonda de cambio de nombre causó crash pre-título, NO repetir. Ejecutar prólogo auténtico; capturar I/O→RAM→GE/VRAM, TEXADDR/CLUT/PRIM y ROI reproducible. Traducir solo tras causalidad con comparación A/B/A.

T: revisar por contexto 9.237 registros, 586 escenas/2.216 cajas, glosario y dos fuentes truncadas. Sincronizar borrador CSV, TXT, bilingüe y guiones en mismo commit; sin editar corpus origen; aprobar texto del HUD, gráficos y prólogo.
G: TUIKA_MES en combate REAL, máscara editables sin recolor CLUT global, 19 glifos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō en menús/HUD/diálogos/batalla con distintas tintas y 2.721 antiguos intactos, seis PNG y 27 IMY sin daños colaterales.
Q: ejecutar los 43 casos inicialmente definidos, ampliar por escenas descubiertas; capturas de PPSSPP auténticas privadas con SHA y trazabilidad PID/ISO, 0 fallos P0/P1, nivel 2, enciclopedia, jefes, guardado-cerrar-reabrir-cargar, finales, regresión de Opciones F1.
F6: solo con 0 textos diferidos, MIPS modelado y QA C completo, construir BPS final con roundtrip y hash, EXE Windows x64 con pruebas negativas E2E, revisión legal de distribución. No subir ISO, BPS comercial, EBOOT, DATA.DAT, IMY, fuentes, sprites, capturas, RAM/GE/VRAM a GitHub público.

## 5. Entrega, GitHub y sucesión

Actualizar sin borrar historia: reports/ESTADO_CONTINUIDAD_PPSSPP.json, reports/COBERTURA_4_AREAS.json, qa/MATRIZ_BETATESTING_COBERTURA.csv, docs/ESTADO_CIERRE_4_AREAS.md y los reportes de hallazgos. No atribuir evidencia C a B; porcentajes solo con numerador/denominador conocido y T/G/Q global NO MEDIBLE si falta censo. Compartir tabla inicial/final, comandos y resultados reales, hashes, evidencias A/B/C, archivos exactos, HEAD, CI push/PR verificados y estado del PR, fallos/rollback.

**AL FINAL: sustituir COMPLETAMENTE prompts/SIGUIENTE_TAREA.md por un relevo R11 autónomo y más concreto, mostrar íntegro su texto, mantener la REGLA RECURSIVA 0 hasta que T/G/R/Q alcancen cada uno el 100% REAL.** No fusionar PR #7 ni afirmar release antes de esa evidencia.

