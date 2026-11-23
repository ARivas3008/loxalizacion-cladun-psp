# CLADUN ES — RELEVO AUTÓNOMO F4/F3-R11: COMPROBAR SEMÁNTICA MIPS 0x0A/0x0B/0x0C Y PRÓLOGO EN PPSSPP REAL

**Corte 23/11/2026.** Repo https://github.com/ARivas3008/loxalizacion-cladun-psp; rama integracion-eventos-segura-20261120, base revision-manual-dialogos, PR #7 OPEN/DRAFT. HEAD confirmado antes del commit documental R10: 7bf03fc9c95b1e5dfac099ae09790f379fc60d58. El commit que publica ESTE PROMPT es posterior; comprueba de nuevo el HEAD final real, las dos ejecuciones CI push/PR y el estado real del PR antes de tocar archivos. Nunca force push ni merge.

Eres equipo sénior de traducción española Cladun, edición indexada IMY/CLUT y fuentes CP932, ingeniería inversa PSP MIPS/ISO9660/PSPFS/DSARC y betatesting PPSSPP oficial 1.20.4. **Ejecuta operaciones, pruebas y cambios reales ahora; no te limites a escribir planes.** Separa A (ISO original auténtica offline), B (código/CI/sintéticos) y C (juego realmente ejecutado); no inventes capturas, PCs, GE/VRAM, hashes, resultados CI, binarios o publicaciones.

## 0. REGLA RECURSIVA INNEGOCIABLE (COPIARLA ÍNTEGRAMENTE EN CADA RELEVO)

**Si cualquiera de los cuatro apartados sigue por debajo del 100 % VERIFICADO, al terminar CADA relevo debes sustituir por completo prompts/SIGUIENTE_TAREA.md en la rama de trabajo mediante un NUEVO prompt autosuficiente y exigirle que haga lo mismo al acabar.** No copies sin actualizar el prompt anterior. Incluye HEAD real, PR y CI reales, estado de cuatro áreas, pruebas A/B/C, hashes reales, archivos concretos, comandos correctos, fallos, hipótesis, tareas no terminadas, próximos criterios de cierre y prohibiciones. Muéstralo íntegro al usuario. Continúa por relevos en nuevas sesiones **solo mientras** existan tareas pendientes; cuando estén **las cuatro al 100 % confirmado**, cambia el entregable a informe final, checklist de lanzamiento y prompt de mantenimiento pospublicación. No generes artificialmente otro relevo de desarrollo tras cierre completo. Si no tienes acceso a GitHub, entrega el archivo nuevo en el chat y marca la escritura remota como NO EJECUTADA.

Si una dependencia bloquea (por ejemplo PPSSPP ausente), ejecuta máxima auditoría segura y tests B, documenta bloqueo preciso y crea siguiente relevo. No confundir B con C ni prometer trabajo en segundo plano.

## 1. ESTADO Y PRUEBA NUEVA R10 — BASE OBLIGATORIA

| Área | Estado real a heredar | Criterio no satisfecho |
|---|---|---|
| T traducción | 9.235/9.237 escritos en borrador (99,98 % escrito, no 100 % contextual) | fuente truncada 008723/008724, glosario, 586 escenas/2.216 cajas, gráficos/prólogo, localización realmente visible |
| G gráficos | NO MEDIBLE global; 6 PNG SYS.DAT2, 27 IMY SYSGRA, 19 glifos A1–B3 sobre 2.721 antiguos | origen visual del prólogo, prueba TUIKA A/B/A en combate y caracteres multicontesto, atlas ROI sin daños |
| R romhacking | 3.724/8.248 sustituciones históricas (45,15% del conjunto), 4.524 pendientes y 85 demo1001 variables bloqueadas | modelo MIPS verdadero, relocalización segura, ISO/BPS y EXE final Windows probado |
| Q betatesting | 45 casos definidos en matriz, Q044/Q045 nuevos, ninguno ejecutado en R10 | PPSSPP C íntegro, completar universo de escenas, reproducibilidad, 0 P0/P1 |

**A — ISO original aportada por el usuario:** archivo 7z original privado. ISO USA exactamente 305.496.064 B y SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f; PSPFS 349. SCRIPT.SDT #231 SHA 1811742d7d3e88da530c1fd2b98885e8426f7af761f7c89aecc80f34ffdbe2d4; SCRIPT.DAT 633344 B SHA c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358; SCRIPT.TBL 52016 B SHA f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37; AISCRIPT.DAT 225488 B SHA 1e75764dcc501f182921039d5020b71b7732d3e2c44b83bb565c70d2297acb3c; AISCRIPT.TBL 17680 B SHA a1bf18abd792494f241f40651c6d11cbff108884c73df07e9a1395566035aede. Se reparsearon 1.625 SCRIPT, 552 AISCRIPT, 51.705 comandos, 46.308 no textuales y 7 bloques demo1001/878 comandos. Identificadores de tablas se solapan en seis casos.

**HALLAZGO NUEVO R10:** tres opcodes con argumentos que coinciden con IDs de SCRIPT.TBL, ninguno coincide con IDs AISCRIPT.TBL: 0x0A (862 comandos, 4B, **320** matches SCRIPT y 183 IDs distintos); 0x0B (166, 5B, **75** matches SCRIPT y 67 IDs; quinto byte 100 en 112, 101 en 54); 0x0C (102, 4B, **86** matches SCRIPT y 49 IDs). **Es un cruce numérico estático y NO demuestra 481 llamadas ni 481 saltos.** El candidato prioritario del R9 sigue scr01.dsf bloque 20 / scriptID 69 / orden20 / offset SCRIPT.DAT decimal 7420, opcode 0x0A / ID instrucción 818 / u32 100100, coincidente con SCRIPT.TBL bloque 758 demo1001_00.dsf. Si un evento de llamada no consume ese argumento, descartar hipótesis y documentarlo.

Los 21 candidatos relativos 0x01/0x02 previos son seis motivos con enteros frecuentes 23/32/55/85; NO tratarlos como saltos. demo1001 tiene 97 textos: 11 mismo tamaño simulados solo en memoria, 85 longitud variable bloqueados, 1 igual; reconstrucción lineal hipotética desplaza 588/878 inicios, +131B netos y al menos 144B extra en tres bloques (padding total 48B). Nada autoriza relocalización.

**B:** herramienta nueva tools/f4_r10_cruce_script_ai.py, tests/test_f4_r10_cruce_script_ai.py con **15 pruebas sintéticas PASS local**, frente a 740 tests Python en CI del HEAD R9 anterior; obtener números y resultados de CI del HEAD FINAL R10 antes de declararlos PASS. La misma función de cruce se ejecutó sobre un parser independiente de la ISO autenticada, informe PRIVADO solo metadatos SHA 385bf2a9471287adebf226a921a4fbf8dd17b7017385ec1da12fb39d577ee7ea. Ver reports/F4_R10_CRUCE_SCRIPT_AISCRIPT_2026-11-23.json y docs/F4_R10_CRUCE_SCRIPT_AISCRIPT_2026-11-23.md.

**C:** NO hubo PPSSPP 1.20.4 real en R10: AppImage ausente y descarga oficial GitHub falló; DNS github.com no resuelve en terminal. Historial F1 llegó a Opciones 756px, mapa 1; NO confundir pasado con nuevo gameplay C. No hay nueva traza MIPS, captura GE ni F3 prólogo traducido.

## 2. LECTURA Y REPRODUCCIÓN

Leer completos antes de editar: AGENTS.md, README.md, CHANGELOG.md, docs/REPRODUCIBILIDAD.md, docs/PROTOCOLO_REINSERCION_FAIL_CLOSED.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md, docs/F4_R10_CRUCE_SCRIPT_AISCRIPT_2026-11-23.md, reports/F4_R10_CRUCE_SCRIPT_AISCRIPT_2026-11-23.json, tools/f4_r10_cruce_script_ai.py, tools/f4_r9_perfil_opcodes.py, tools/f4_referencias_demo1001.py, tools/f3_referencias_riesgo.py, tools/script_event_guard.py, tools/f3_anclar_intro.py, tools/f3_simular_intro_mismo_tamano.py, tools/f3_presupuesto_padding_intro.py, docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md, docs/F3_R6_PADDING_ORIGINAL_Y_CAPACIDAD_2026-11-23.md, docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md, reports/COBERTURA_4_AREAS.json, reports/ESTADO_CONTINUIDAD_PPSSPP.json, qa/MATRIZ_BETATESTING_COBERTURA.csv, docs/ESTADO_CIERRE_4_AREAS.md y este prompt.

Si existe checkout válido:

    git fetch origin
    git switch integracion-eventos-segura-20261120
    git pull --ff-only
    git rev-parse HEAD
    git status --short
    python -m unittest discover -s tests -v
    python -m unittest discover -s tests -p 'test_f4_r10_cruce_script_ai.py' -v
    python tools/qa_cobertura_4_areas.py
    python tools/qa_cobertura_4_areas.py --require-closed  # DEBE FALLAR con áreas pendientes
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
    (cd patcher && go test ./...)
    git diff --check

Con ISO privada SHA exacto y sin reutilizar nombres de informes:

    python tools/f4_r10_cruce_script_ai.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/R11_CRUCE_NUEVO.json

Si falla git clone/pull por DNS, usar conector GitHub para lectura y commit no forzado con comprobación de HEAD; no declarar suite local completa sin checkout.

## 3. P0 — PPSSPP/PSP MIPS, NO SIMULACIONES

Recuperar PPSSPP **oficial v1.20.4 Linux x86_64** desde release verificada de hrydgard/ppsspp (asset PPSSPP-v1.20.4-anylinux-x86_64.AppImage). Hash histórico exacto AppImage SHA 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21; comparar hash descargado antes de ejecutar. Si no puede descargarse, registrar limitación y avanzar con estáticos sin inventar C. ISO original SHA exacto y espacio PRIVADO. Autenticar binario PPSSPP, PID/starttime, FD de la ISO, mismo PID propietario del WebSocket 24192, backend y versión. No publicar capturas comerciales o volcados RAM/GPU.

F4-a: reproducir escenificación original de scr01.dsf donde se consuma efectivamente comando offset SCRIPT.DAT 7420. Ubicar en RAM la estructura cargada y medir PC MIPS, registros, u32 100100, transición script origen→destino y retorno; NO asumir RAM_addr=7420. Comparar A/B/A solo si sonda controlada no rompe arranque. Dejar semántica UNKNOWN si no hay ejecución. El contexto anterior en origen contiene 0xFA/ID817 antes de 0x0A/ID818, y después 0x05/ID818 y 0x08/ID820; esto es orden de instrucciones, no interpretación.

F4-b: instrumentar **0x0B** con argumento u32+0 y quinto byte 100/101; distinguir control/estado de datos, medir ejecución real y retornos. Investigar **0x0C** del mismo modo, contrastar SCRIPT.TBL y AISCRIPT.TBL; controlar seis IDs presentes en ambas tablas. No decidir que 0x0B/0x0C son subrutinas por tasa de igualdades. Cubrir referencias externas, ordinales, saltos de 16 bits y tablas indirectas.

F4-c: solo si semántica de todas las referencias y retorno están demostradas, hacer primera relocalización privada reversible de un evento variable, con diff por opcode/ID/argumentos no textuales y offsets, PPSSPP A/B/A y rollback. Mantener 85 demo1001 y 4.524 globales BLOQUEADOS mientras falte prueba; nunca desactivar --event-safe-only por comodidad.

## 4. P0 F3 GRÁFICOS Y P1 T/G/Q/F6

F3: frase inglesa real "Some say, because the treasures were there." NO localizada; ANIME000.IDT contiene 231 firmas IMY (136 tipo00/95 tipo02), no frames ni letras identificados. La antigua sonda de cambiar nombre ANIME000 provocó crash pre-título; NO repetir. En PPSSPP llegar a prólogo auténtico y vincular I/O→descompresión→RAM→GE/VRAM con textura/CLUT/PRIM. Si bitmap, ROI/paleta local y A/B/A; si script, ID/off real. No asumir que demo1001 contiene letras del prólogo.

T: terminar 9.237 registros y comprobar por escena 586 escenas/2.216 cajas, glosario canónico, variables/acentos y 008723/008724 sin inventar texto cortado. Sincronizar CSV/TXT/guiones sin editar corpus origen y revisar todos los gráficos textuales antes de T=100%.

G: mantener fuentes CP932 con 2.721 originales +19 nuevos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō y white_new_ink=False; TUIKA_MES.IMY 256×256 4bpp, CLUT2 afecta 9.144 texeles, 3.506 protegidos. No cambio global CLUT; experimentar solo ROI sin daños y combate auténtico, tintas y menús/HUD. Seis PNG SYS.DAT2 y 27 IMY SYSGRA cubiertos parcialmente, inventario total aún no certificado.

Q: matriz con **45 casos** Q001–Q045, nueva Q044 (0x0B+quinto byte) y Q045 (0x0C y namespaces) NOT_RUN. Ampliar casos reales, obtener ISO/PPSSPP SHA y captura privada autenticada por escenario, cubrir primer/segundo nivel, batalla, enciclopedia, retratos/tiles/audio, guardar/cerrar/reabrir/cargar, final/créditos, controles Opciones, sin P0/P1 para cierre.

F6: al lograr T/G/R/Q=100% real, generar BPS original→candidata segura, roundtrip Go/Python y hashes exactos, EXE Windows x64 E2E con errores negativos y revisión legal. Nunca versionar ISO, BPS que reproduzca juego comercial, DATA.DAT, EBOOT, fuentes, IMY, sprites, RAM/GE/VRAM ni capturas con contenido del juego.

## 5. ENTREGABLE Y CONTINUIDAD RECURSIVA

Actualizar reports/COBERTURA_4_AREAS.json, reports/ESTADO_CONTINUIDAD_PPSSPP.json sin borrar historia, qa/MATRIZ_BETATESTING_COBERTURA.csv, docs/ESTADO_CIERRE_4_AREAS.md y evidencias A/B/C. Documentar herramientas, comandos, hashes, errores/rollback, porcentaje con denominador real, sin declarar cierres basados en tests B. Comprobar PR #7 OPEN/DRAFT, HEAD final y workflows push/PR reales tras publicación.

**AL FINAL, SI EXISTE UN SOLO PENDIENTE, REEMPLAZA COMPLETAMENTE prompts/SIGUIENTE_TAREA.md por un nuevo prompt autónomo R12 con la MISMA REGLA RECURSIVA 0, nuevos hallazgos, prioridades y comandos correctos, y MUESTRA EL TEXTO ÍNTEGRO AL USUARIO.** Si se completan realmente T/G/R/Q, emitir informe de cierre y prompt de mantenimiento, no inventar otro relevo de desarrollo.

