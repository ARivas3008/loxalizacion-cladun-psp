# CLADUN ES — RELEVO AUTÓNOMO F4/F3-R13: DEMOSTRAR ID+100 Y VALORES ESPECIALES CON MIPS REAL, T/G/R/Q ABIERTAS

**Corte 23/11/2026.** Repositorio https://github.com/ARivas3008/loxalizacion-cladun-psp. Rama `integracion-eventos-segura-20261120`; PR #7 OPEN/DRAFT, base `revision-manual-dialogos`. HEAD verificado al comienzo R12: `41d9a235ff332d0c05efe7c4ce8deb91b386b9e7`. Commit del código R12: `5c6c109356b706838317926c6873e4e49f06abcc`. El commit FINAL documental R12 es POSTERIOR: leer de nuevo HEAD, estado PR y Actions push/PR del SHA FINAL; no atribuir resultados anteriores. Nunca force push, rebase destructivo ni merge prematuro.

Actúa como ingeniero sénior de PSP MIPS, PPSSPP **oficial v1.20.4**, ISO9660/PSPFS/DSARC y fuentes/texturas IMY/CLUT, codificación CP932 A1–B3, traducción española natural y betatesting. **Ejecuta pruebas y cambios REALES AHORA, no escribas solo un plan.** Clasifica evidencia **A** (ISO USA original privada), **B** (pruebas de código/sintéticos/CI) y **C** (gameplay autenticado PPSSPP). No inventes PCs MIPS, registros, texturas, screenshots, hashes, pasos, CI ni finalización.

## 0. REGLA RECURSIVA INNEGOCIABLE — COPIAR ENTERA

**Si cualquiera de los cuatro apartados sigue por debajo del 100 % VERIFICADO, al terminar CADA relevo debes sustituir por completo prompts/SIGUIENTE_TAREA.md en la rama de trabajo mediante un NUEVO prompt autosuficiente y exigirle que haga lo mismo al acabar.** No copies sin actualizar el prompt anterior. Incluye HEAD real, PR y CI reales, estado de cuatro áreas, pruebas A/B/C, hashes reales, archivos concretos, comandos correctos, fallos, hipótesis, tareas no terminadas, próximos criterios de cierre y prohibiciones. Muéstralo íntegro al usuario. Continúa por relevos en nuevas sesiones **solo mientras** existan tareas pendientes; cuando estén **las cuatro al 100 % confirmado**, cambia el entregable a informe final, checklist de lanzamiento y prompt de mantenimiento pospublicación. No generes artificialmente otro relevo de desarrollo tras cierre completo. Si no tienes acceso a GitHub, entrega el archivo nuevo en el chat y marca la escritura remota como NO EJECUTADA.

Si PPSSPP o una dependencia impide C, realizar máxima auditoría segura A y tests B, describir bloqueo y su condición de desbloqueo, crear R14. Nunca sustituir C por B. No prometer trabajo asíncrono.

## 1. ESTADO INICIAL, BASE REAL Y HALLAZGO MÁS RECIENTE

T traducción: 9.235/9.237 filas con español escrito (~99,98 % borrador, NO calidad final). Faltan revisión contextual completa en 586 escenas/2.216 cajas, glosario, dos originales truncados 008723/008724, textos gráficos/prólogo y pruebas de escena/acentos. Denominador total visible no certificado.

G gráficos: NO MEDIBLE global; se auditaron históricamente 6 PNG SYS.DAT2, 27 IMY SYSGRA, 19 caracteres españoles A1–B3 añadidos a 2.721 glifos originales. TUIKA_MES.IMY 256×256 4bpp, 9.144 texeles CLUT2 con 3.506 en subregiones protegidas. Faltan procedencia inglesa del prólogo, máscaras ROI protegidas, TUIKA en combate y visualización de 19 glifos multicontesto/varias tintas. `white_new_ink=False`, prohibido recolor global CLUT2.
R romhacking: 3.724/8.248 (45,15 %) cambios en candidata experimental protegida histórica; **4.524 diferenciados en longitud** siguen BLOQUEADOS. 97 textos intro demo1001: 11 mismo tamaño solo simulados RAM, 85 variables bloqueados, 1 igual; modelo lineal movería 588/878 inicios y faltan al menos 144B para tres bloques alineados frente a 48B padding. Cero relocalizaciones variables MIPS certificadas, no BPS/EXE final.
Q betatesting: matriz ampliada de 47 a **49 casos Q001–Q049**, nuevos Q048 y Q049 NOT_RUN; 0 C nuevos en R12, universo completo NO MEDIBLE; tampoco certificación Windows GUI E2E, finales ni ciclo guardar/cerrar/cargar.

**A ISO ORIGINAL AUTHENTICADA R12:** extraída privadamente de /mnt/data/Cladun_This_Is_An_RPG_USA_PSN_PSP-PLAYASiA.7z en el turno anterior; NO asumir que esas rutas persistan. ISO USA 305.496.064 bytes SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`; DATA.DAT PSPFS 349, SCRIPT.DAT 633344 bytes SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`; SCRIPT.TBL 52016 bytes SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. 1625 bloques SCRIPT, 51705 comandos, 46308 no textuales, 552 scripts AISCRIPT; ID=0 AUSENTE de SCRIPT.TBL. Original sin ninguna edición.

**Hallazgo F4 R12 NUEVO y corrección del enfoque R11:**
- opcode **0x0A** 862 comandos: **860** argumentos `u32−100` iguales a IDs de SCRIPT.TBL; dos u32 restantes son **0** y **1** (uno cada), ambos en `atkDefComment.dsf`, bloque 1581, órdenes9/11, offsets SCRIPT.DAT 626762/626776.
- opcode **0x0B** 166: **158** ID−100 coincidentes; ocho u32 **3**, todos en dos bloques `mo_atk.dsf` 337/338, offsets 100889,100909,100929,100949,101060,101083,101119,101142. Quinto byte 100 en112 instrucciones (104 coinciden, 8 no), 101 en54 (54 coinciden).
- opcode **0x0C** 102: **66** ID−100 coincidentes, restantes **36** con valor u32 **100**, distribuidos en **34 bloques** y 31 nombres (incluye demo1001). Puesto que ID0 no existe, `100−100=0` no es un ID de script. R11 veía 86 coincidencias literales para 0x0C; podrían ser coincidencias por el valor repetido 100 que sí es ID de otro script. **NO afirmar que 0x0C no usa ID+100 por aquella comparación.**
- **CUIDADO:** "sugerido ID+100" NO significa llamada, salto, valor nulo o fin de evento demostrado. Clasificar los 46 u32 no coincidentes como VALORES SIN COINCIDENCIA, no como centinelas funcionales certificados.
- **Ancla para MIPS:** `scr01.dsf`, origen bloque20/orden20, offset SCRIPT.DAT7420, opcode 0x0A/ID818, u32=100100. Con regla candidata `−100`, destino ID100000/bloque757 `demo1001_00.dsf`; con literal, ID100100/bloque758; falta traza PPSSPP para elegir.
- Relevo R12 nuevo `tools/f4_r12_candidatos_especiales.py` y `tests/test_f4_r12_candidatos_especiales.py`, **17 tests B sintéticos PASS local**; función aplicada a 51705 comandos auténticos por parser independiente. Informe privado de metadatos SHA256 `c858d33ac0ef8d23186a86f95997bfaea5d608518e7195fc8aa40995b09d4a54`. Ver `reports/F4_R12_CANDIDATOS_ESPECIALES_2026-11-23.json`, `docs/F4_R12_CANDIDATOS_ESPECIALES_2026-11-23.md`. Verificar CI HEAD final real; el número de tests de CI no se presume.
- **C R12 NO EJECUTADA**: ni AppImage PPSSPP 1.20.4 oficial ni descarga GitHub accesibles desde terminal; no PC MIPS, no RAM/GE/VRAM, no capturas nuevas.

## 2. PASOS Y COMANDOS REPRODUCIBLES

Leer antes de editar: `AGENTS.md`, `README.md`, `CHANGELOG.md`, `docs/REPRODUCIBILIDAD.md`, `docs/PROTOCOLO_REINSERCION_FAIL_CLOSED.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md`, `docs/F4_R12_CANDIDATOS_ESPECIALES_2026-11-23.md`, `reports/F4_R12_CANDIDATOS_ESPECIALES_2026-11-23.json`, `tools/f4_r12_candidatos_especiales.py`, `tools/f4_r11_desfase_ids.py`, `tools/f4_r10_cruce_script_ai.py`, `tools/f4_r9_perfil_opcodes.py`, `tools/f4_referencias_demo1001.py`, `tools/f3_referencias_riesgo.py`, `tools/script_event_guard.py`, `docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md`, `docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/ESTADO_CIERRE_4_AREAS.md`, y este prompt. No sobrescribir corpus original ni duplicar validaciones.

Si existe checkout real:

```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p 'test_f4_r12_candidatos_especiales.py' -v
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # debe seguir FALLANDO con 4 áreas abiertas
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
```

Con ISO exacta autenticada en carpeta **PRIVADA**, sin nombres de reporte ya usados:

```bash
python tools/f4_r12_candidatos_especiales.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F4_R13_SONDA_NUEVA.json
```

Sin git local por DNS, usar el conector GitHub (lectura HEAD, commit no forzado, verificación push/PR CI). Nunca inventar ejecución local de suite completa.

## 3. P0: PPSSPP AUTÉNTICO Y MIPS — DISCRIMINAR CONTROL DE FLUJO

Obtener PPSSPP **oficial v1.20.4 Linux x86_64 AppImage** desde fuente verificable; SHA256 histórico del binario `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. Comprobar el archivo antes de ejecutar. Si no está accesible, **NO producir pruebas C**. Ejecutar original ISO privada SHA exacto con PID/starttime y FD a ese ISO comprobados, socket WS24192 propietario del MISMO PID, backend y captura auténtica. Usar traza real para determinar RAM base del script y PC MIPS; **offset SCRIPT.DAT no equivale a RAM addr**.

Prioridad F4:
1. En ejecución de `scr01.dsf`, observar lectura comando offset7420 opcode0x0A ID818 con u32=100100; comprobar si se resuelve a scriptID100000/bloque757, ID100100/bloque758 o diferente. Registrar PC, registros, stack/estado, retorno y prueba A/B/A.
2. Instrumentar `atkDefComment.dsf` bloque1581 órdenes9/11, valores u32 0 y 1 de opcode0x0A. No etiquetar significado sin observación C.
3. En `mo_atk.dsf` bloques337/338 investigar las ocho u32=3 de opcode0x0B y quinto byte100; comparar contra 0x0B con quinto byte101 y con ID−100 válido.
4. Prioridad NUEVA `0x0C` u32=100: 36 comandos en 34 bloques/31 nombres, entre ellos intro demo1001. Contrastar control real de ese argumento y un 0x0C con ID−100 válido. Comprobar si el valor 100 tiene efecto especial o es dato ordinario.
5. Continuar explorando posibles referencias de 16 bits, ordinales, offsets, punteros y retornos. No asumir que hallar coincidencia con ID prueba ausencia de referencias ocultas.
6. SOLO tras demostrar semántica completa y seguridad de todas las referencias, experimentar con **una** relocalización variable privada reversible, reparsear 51.705 comandos, comprobar equivalencia byte a byte de 46.308 no-textos y todas las entradas PSPFS vecinas, PPSSPP A/B/A y rollback. Hasta entonces **NO liberar 85 intro variables ni 4524 globales; mantener `--event-safe-only`**.

## 4. F3/F2, TRADUCCIÓN, GRÁFICOS, QA Y DISTRIBUCIÓN

F3: frase en inglés del prólogo `Some say, because the treasures were there.` sin procedencia visual/script identificada. ANIME000.IDT muestra 231 firmas IMY (136 tipo00, 95 tipo02), NO frames probados; renombrarlo causó crash pre-título y NO debe repetirse. PPSSPP original, escena exacta → archivo I/O→RAM→GE/VRAM→ TEXADDR/CLUT/PRIM; distinguir bitmap/ROI/script, intervención local sin recolor global, comparar A/B/A.

T: revisar 9.237 textos, glosario, 586 escenas/2.216 cajas, naturalidad, tildes/variables/fuentes truncadas 008723/008724; sincronizar CSV/TXT/guiones, proteger corpus fuente. No declarar T=100 sin revisar textos gráficos y todo contenido visible en juego.

G: TUIKA_MES.IMY 256×256 4bpp, CLUT2 9144 texeles (3506 de regiones protegidas), no alterar CLUT global. Fuente 2721 originales +19 A1–B3 `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` con `white_new_ink=False`; verificar en diálogos, HUD, Opciones y combate con varias tintas, antes de aprobar edición gráfica total.

Q: matriz **49 casos Q001–Q049**, Q048 `0x0C` u32=100 y Q049 `0x0A` u32=0/1 NOT_RUN. Ampliar universo por escenas y rutas completas; recorrer segundo nivel, combate/TUIKA, inventario/enciclopedia, guardado-cerrar-reabrir-cargar, créditos y finales, sprites/tiles/retratos/audio, test regresión Opciones F1. Evidencia C screenshots privados con SHA y trazabilidad PID/ISO/PPSSPP; 0 P0/P1 para cierre.

F6 SOLO con cuatro áreas 100% demostrado: BPS diferencial desde ISO original con roundtrip y SHA autenticados; EXE Windows x64 interfaz E2E, negativos e integridad; revisar legalidad de distribución. No publicar ISO, DATA.DAT, EBOOT, BPS con assets comerciales, FONT/IMY/sprites, capturas o dumps RAM/GE/VRAM. No merge PR#7 antes del cierre.

## 5. ENTREGABLE OBLIGATORIO Y SIGUIENTE RELEVO

Actualizar sin borrar la historia `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, `docs/ESTADO_CIERRE_4_AREAS.md`, informes nuevos y tests; compartir tabla antes/después T/G/R/Q con numeradores, denominadores y NO MEDIBLE cuando corresponda. Verificar HEAD, PR y ambos workflows del HEAD final; documentar A/B/C, ISO y hashes, fallos, rollback, archivos/commits exactos.

**AL CONCLUIR, SI QUEDA ALGO BAJO 100% VERIFICADO, REEMPLAZAR COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` POR UN NUEVO PROMPT AUTÓNOMO R14, COPIANDO ÍNTEGRAMENTE REGLA RECURSIVA 0, Y MOSTRAR SU TEXTO COMPLETO AL USUARIO.** Al lograr realmente T/G/R/Q=100, entregar informe de lanzamiento y prompt de mantenimiento, nunca inventar otro relevo de desarrollo.

