# CLADUN ES — RELEVO AUTÓNOMO F4/F3-R12: PROBAR ID+100 EN MIPS, NO ASUMIR SALTOS; T/G/R/Q ABIERTAS

**Corte: 23/11/2026.** Repositorio https://github.com/ARivas3008/loxalizacion-cladun-psp; rama \`integracion-eventos-segura-20261120\`, PR #7 OPEN/DRAFT contra \`revision-manual-dialogos\`. HEAD inicial comprobado en R11: \`d287b766461dbd796a810be3163b4e47663efe72\`. Código del hallazgo R11: \`2aa9d5d7531f958ecd25b4c65092534b0a7c0ae9\`. EL COMMIT FINAL R11 es posterior: verificar HEAD efectivo y CI del commit final antes de escribir; no force push ni merge.

Eres especialista sénior PSP MIPS, PPSSPP 1.20.4, ISO9660/PSPFS/DSARC, IMY/CLUT, codificación A1–B3, traducción natural española y QA. Ejecuta cambios/pruebas reales en el turno y documéntalos, no solo consejos. Clasifica A=ISO auténtica offline, B=sintéticos/CI, C=juego ejecutado PPSSPP oficial. No inventes capturas, MIPS PC, RAM/VRAM/GE, éxito de pruebas, hashes ni confirmación de relocalización.

## 0. REGLA RECURSIVA INNEGOCIABLE (copiar COMPLETA en siguiente relevo)

**Si cualquiera de los cuatro apartados sigue por debajo del 100 % VERIFICADO, al terminar CADA relevo debes sustituir por completo prompts/SIGUIENTE_TAREA.md en la rama de trabajo mediante un NUEVO prompt autosuficiente y exigirle que haga lo mismo al acabar.** No copies sin actualizar el prompt anterior. Incluye HEAD real, PR y CI reales, estado de cuatro áreas, pruebas A/B/C, hashes reales, archivos concretos, comandos correctos, fallos, hipótesis, tareas no terminadas, próximos criterios de cierre y prohibiciones. Muéstralo íntegro al usuario. Continúa por relevos en nuevas sesiones **solo mientras** existan tareas pendientes; cuando estén **las cuatro al 100 % confirmado**, cambia el entregable a informe final, checklist de lanzamiento y prompt de mantenimiento pospublicación. No generes artificialmente otro relevo de desarrollo tras cierre completo. Si no tienes acceso a GitHub, entrega el archivo nuevo en el chat y marca la escritura remota como NO EJECUTADA.

Si hay bloqueo de PPSSPP, ejecuta máximo análisis seguro sobre ISO original y tests B, deja bloqueo concreto y genera relevo. Nunca sustituir C por B ni prometer trabajo en segundo plano.

## 1. ESTADO BASE R11, RESULTADO A NUEVO Y CORRECCIÓN DE HIPÓTESIS

T: **9.235/9.237 filas de borrador escritas (99,98%)**, NO 100% de calidad/narrativa en juego. Dos orígenes truncados 008723/008724 y prólogo gráfico sin localización acreditada; 586 escenas/2.216 cajas requieren cierre contextual.
G: inventario global NO MEDIBLE; 6 PNG SYS.DAT2 y 27 IMY SYSGRA históricos, 19 glifos A1–B3 más 2.721 originales, TUIKA_MES 9.144 texeles CLUT2 con 3.506 en subregiones protegidas. Faltan ROI, combate auténtico y 19 caracteres multicontesto.
R: **3.724/8.248 (45,15%)** sustituciones del experimento protegido, **4.524 difieren en longitud y siguen BLOQUEADAS**. De 97 textos demo1001, 11 misma longitud simulado RAM-only, 85 variables bloqueados y 1 idéntico. Reconstrucción hipotética desplazaría 588/878 inicios, +131 bytes netos, 48 bytes de padding original y +144 bytes mínimos extra para tres bloques. No BPS+EXE release.
Q: **47 casos Q001–Q047 definidos**, nuevos Q046 y Q047 NOT_RUN, universo completo NO MEDIBLE, ninguno pasado durante R11 en PPSSPP. No convertir regresiones históricas en PASS de la candidata final.

**A REAL:** ISO USA original auténtica 305496064 bytes SHA256 \`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f\`, DATA.DAT/349 PSPFS. SCRIPT.DAT 633344 bytes SHA \`c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358\`, SCRIPT.TBL 52016 SHA \`f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37\`. 1.625 bloques/51.705 comandos/46.308 no textuales. AISCRIPT.TBL 552 IDs, seis coinciden con IDs de SCRIPT.TBL. Original comercial sin cambios.

**HALLAZGO R11 QUE CORRIGE R9/R10:** barrido del u32 de opcodes 0x0A/0x0B/0x0C contra todos los SCRIPT IDs, evaluando \`argumento - delta\` para delta [-256,256]:
- 0x0A: coincidencia literal **320/862**, pero \`argumento−100\` está en tabla para **860/862**. Las dos excepciones son valores 0 y 1 (una de cada). Delta 99 da 735; delta 101 da 426. Hay 278 IDs distintos bajo delta 100.
- 0x0B: literal **75/166**, delta 100 **158/166**; las ocho excepciones son valor 3. Delta 99 y 101 dan 101 cada uno. Hay 139 IDs distintos bajo delta 100; byte quinto observado históricamente vale 100 o 101, NO se sabe significado.
- 0x0C: literal **86/102** frente a delta100 **66/102**; su máximo del barrido es delta0 con 86, delta90 con 82. **NO imponer +100 globalmente.**

**CORRECCIÓN CRÍTICA DEL ANCLA:** comando auténtico \`scr01.dsf\`, scriptID 69, bloque20, orden20, offset SCRIPT.DAT **7420**, opcode 0x0A, instructionID818, u32=100100. R9 decía destino literal scriptID100100/bloque758; bajo el patrón global 0x0A, el candidato mejor sustentado es **scriptID100000/bloque757 (\`demo1001_00.dsf\`)**. Ni uno ni otro está confirmado con MIPS. El valor u32 no es una dirección RAM. NO editar ni reubicar por esta hipótesis.

Herramienta R11 \`tools/f4_r11_desfase_ids.py\`, pruebas \`tests/test_f4_r11_desfase_ids.py\` (**15 sintéticos PASS local**), informe \`reports/F4_R11_DESFASE_IDS_2026-11-23.json\` y \`docs/F4_R11_DESFASE_IDS_2026-11-23.md\`. La misma función se ejecutó sobre 51.705 comandos extraídos desde la ISO auténtica por parser independiente, sin modificar ISO. Informe privado SHA256 \`5cf5f3e1f7b61f1bcb1ca6b41154cab091e03dde2b2ebcd69015ce0d33bad79b\`. El informe público solo incluye metadatos. **B/CI del HEAD R11 final: VERIFICAR AHORA, no suponer éxito. C R11: NO EJECUTADO**, PPSSPP 1.20.4 AppImage ausente, terminal sin DNS a github.com y descarga alternativa fallida.

## 2. LECTURA OBLIGATORIA, COMANDOS Y AUDITORÍA PRIVADA

Antes de editar leer \`AGENTS.md\`, \`README.md\`, \`CHANGELOG.md\`, \`docs/REPRODUCIBILIDAD.md\`, \`docs/PROTOCOLO_REINSERCION_FAIL_CLOSED.md\`, \`docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md\`, \`docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md\`, \`docs/F4_R11_DESFASE_IDS_2026-11-23.md\`, \`reports/F4_R11_DESFASE_IDS_2026-11-23.json\`, \`tools/f4_r11_desfase_ids.py\`, \`tools/f4_r10_cruce_script_ai.py\`, \`tools/f4_r9_perfil_opcodes.py\`, \`tools/f4_referencias_demo1001.py\`, \`tools/f3_referencias_riesgo.py\`, \`tools/script_event_guard.py\`, \`docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md\`, \`docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md\`, \`qa/MATRIZ_BETATESTING_COBERTURA.csv\`, \`reports/COBERTURA_4_AREAS.json\`, \`reports/ESTADO_CONTINUIDAD_PPSSPP.json\`, \`docs/ESTADO_CIERRE_4_AREAS.md\` y este prompt.

Con checkout real (no fingirlo si DNS falla):

\`\`\`bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git rev-parse HEAD
git status --short
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p 'test_f4_r11_desfase_ids.py' -v
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # DEBE FALLAR
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
\`\`\`

Con ISO original en carpeta PRIVADA fuera de Git, no reutilizar reporte:

\`\`\`bash
python tools/f4_r11_desfase_ids.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F4_R12_DESFASE_NUEVO.json
\`\`\`

Si falla DNS terminal, usar conector GitHub para lecturas/commits no forzados y comprobar CI push/PR del SHA publicado; no declarar suite local completa sin checkout.

## 3. P0 — DECODE ID+100 Y CONTROL DEL INTÉRPRETE EN PPSSPP REAL

Recuperar **PPSSPP v1.20.4 OFICIAL** Linux x86_64; hash histórico AppImage \`661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21\`. Verificar binario/hash antes de ejecución, ISO USA SHA exacto, PID/starttime, FD ISO abierto, WebSocket 24192 del MISMO PID, backend y captura original X11. Si AppImage inaccesible, NO generar captura sintética ni declarar C.

**F4-a: discriminar destino 757 frente a 758.** Reproducir el comando real de scr01.dsf bloque20/orden20/offset7420, observar acceso u32=100100 en RAM, PC MIPS real, registros/función de dispatch y la consulta efectiva SCRIPT.TBL. Verificar si el motor aplica \`id=argumento−100\` y selecciona bloque **757** / ID100000, selecciona literal bloque 758 o ejecuta otro mecanismo. Registrar antes/después de estado y retorno, repetir con control no destructivo. Si no hay ejecución, conservar AMBAS hipótesis y bloqueo.

**F4-b: investigar casos especiales y otros opcodes.** En 0x0A localizar los casos u32 0 y 1 y comprobar significado en runtime. En 0x0B analizar argumento−100 para 158 casos y ocho casos de u32 3; controlar quinto byte 100/101 por comparación MIPS. 0x0C debe estudiarse separadamente: 86 literales frente a 66 desplazados, no hay evidencia de offset uniforme. Revisar referencias de 16 bits/ordinales, llamadas, retornos, cambio de bloque y tablas externas antes de diseñar relocalizador.

**F4-c: no cambiar diálogos variables** ni reconstruir SCRIPT.DAT hasta tener modelo de todas las referencias y prueba A/B/A auténtica de un evento protegido, reparseo completo de 51.705 comandos y byte-exact de no-textos. Conservar \`--event-safe-only\`, 4.524 diferidos, 85 variables demo1001.

## 4. P0 F3, F2 Y CIERRES T/G/Q/F6

**Prólogo F3:** la frase inglesa visible \`Some say, because the treasures were there.\` sigue sin fuente gráfica/script demostrada. ANIME000.IDT 231 cabeceras IMY (136 tipo00, 95 tipo02) no son frames ni prueba de letras; renombrar el archivo causó crash pre-título, NO repetir. PPSSPP auténtico → I/O→RAM→GE/VRAM, CLUT/TEXADDR/PRIM → identificar ROI si bitmap o script exacto; A/B/A original/sonda/original sin romper otros recursos.

**Traducción T:** auditar 9.237 registros, 586 escenas/2.216 cajas, glosario, acentos/variables/idioma natural y dos orígenes truncados 008723/008724 sin inventar fuente. Sincronizar borrador CSV/TXT/guiones; original corpus inmutable, texto en gráficos incluido en denominador final.

**Gráficos G:** seis PNG SYS.DAT2 y 27 IMY SYSGRA; \`TUIKA_MES.IMY\` 256x256 4bpp CLUT2 afecta 9.144 texeles, 3.506 protegidos; prohibido recolor global. Verificar TUIKA en combate real, máscaras ROI y 19 glifos \`áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō\` en todos los contextos con distintas tintas, mantener 2.721 glifos originales y \`white_new_ink=False\`.

**Betatesting Q:** completar matriz \`qa/MATRIZ_BETATESTING_COBERTURA.csv\` (47 casos, denominador aún no total), Q046 literal-vs-menos100 y Q047 u32=3 0x0B NOT_RUN, además combate, segundo nivel, enciclopedia, guardado-cerrar-cargar, audios, retratos, tiles, final, regresión F1 opciones; capturas reales privadas con SHA y PID/ISO/PPSSPP autenticados, cero P0/P1 para cierre.

**F6 release:** SOLO tras T/G/R/Q 100% con evidencia C, 0 textos pendientes, generar BPS original→candidata, roundtrip Go/Python SHA exactos, EXE Win64 GUI E2E y negativos, revisión legal. No subir ISO, DATA.DAT, EBOOT, IMY, FONT, sprites, capturas, RAM/GE ni BPS con activos comerciales.

## 5. ENTREGA Y RECURSIVIDAD

Actualizar sin perder historia \`reports/COBERTURA_4_AREAS.json\`, \`reports/ESTADO_CONTINUIDAD_PPSSPP.json\`, \`qa/MATRIZ_BETATESTING_COBERTURA.csv\`, \`docs/ESTADO_CIERRE_4_AREAS.md\` e informes A/B/C. Tabla de T/G/R/Q antes/después con denominadores reales, bloqueos, comandos, tests y hashes, HEAD y workflows reales del final, PR #7 DRAFT y sin merge. No adjudicar PASS C a estadísticas A ni CI B.

**AL TERMINAR REEMPLAZAR ÍNTEGRAMENTE \`prompts/SIGUIENTE_TAREA.md\` POR UN NUEVO RELEVO AUTÓNOMO R13 CON ESTA MISMA REGLA RECURSIVA 0; PUBLICARLO EN GITHUB Y MOSTRAR SU TEXTO ÍNTEGRO AL USUARIO.** Solo al cerrar realmente las cuatro áreas, pasar a informe final de release y mantenimiento, no generar más relevos de desarrollo.

