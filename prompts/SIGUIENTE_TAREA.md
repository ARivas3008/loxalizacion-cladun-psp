# CLADUN ES — RELEVO AUTÓNOMO F4/F3-R14: DEMOSTRAR EJECUCIÓN DEL GRAFO DEL PRÓLOGO Y RUTAS 0x0A/0x0C; CUATRO ÁREAS ABIERTAS

**Corte 23/11/2026.** Repo https://github.com/ARivas3008/loxalizacion-cladun-psp. Rama de trabajo `integracion-eventos-segura-20261120`, base `revision-manual-dialogos`, PR #7 OPEN/DRAFT. HEAD comprobado al comienzo de R13: `cc335be8939214a9202ca324901b7e4ee3cc0a6c`. Commit del código R13: `1bc8baae4ff94f1fc88a5b37ac7d8c5532edb7cc`. El commit DOCUMENTAL que contiene este prompt será posterior: siempre consultar SHA real antes/después y Actions push/PR del HEAD final. No modificar base, no force push, no rebase destructivo, no merge prematuro.

Eres ingeniero sénior en PSP MIPS, PPSSPP oficial 1.20.4, ISO9660/PSPFS/DSARC, IMY/CLUT, fuentes CP932 A1–B3, localización española y betatesting. **Ejecuta código y pruebas reales, cambios justificados y documentación en este turno**. Separa evidencia **A** original ISO autentificada, **B** tests sintéticos/código/CI y **C** juego ejecutado en PPSSPP oficial. Nunca inventar PC MIPS, instrucciones GE, capturas, hashes, éxito CI, binarios ni cierres.

## 0. REGLA RECURSIVA INNEGOCIABLE (COPIARLA ÍNTEGRA EN CADA SIGUIENTE PROMPT)

**Si cualquiera de los cuatro apartados sigue por debajo del 100 % VERIFICADO, al terminar CADA relevo debes sustituir por completo prompts/SIGUIENTE_TAREA.md en la rama de trabajo mediante un NUEVO prompt autosuficiente y exigirle que haga lo mismo al acabar.** No copies sin actualizar el prompt anterior. Incluye HEAD real, PR y CI reales, estado de cuatro áreas, pruebas A/B/C, hashes reales, archivos concretos, comandos correctos, fallos, hipótesis, tareas no terminadas, próximos criterios de cierre y prohibiciones. Muéstralo íntegro al usuario. Continúa por relevos en nuevas sesiones **solo mientras** existan tareas pendientes; cuando estén **las cuatro al 100 % confirmado**, cambia el entregable a informe final, checklist de lanzamiento y prompt de mantenimiento pospublicación. No generes artificialmente otro relevo de desarrollo tras cierre completo. Si no tienes acceso a GitHub, entrega el archivo nuevo en el chat y marca la escritura remota como NO EJECUTADA.

Si PPSSPP oficial no está disponible, hacer la máxima auditoría segura A y tests B, registrar bloqueo y condición exacta para reanudar C; publicar prompt R15. B jamás sustituye C. No prometer trabajo asíncrono.

## 1. ESTADO T/G/R/Q R13 y NUEVO MAPA F4

- **Traducción T**: 9.235 de 9.237 textos escritos en borrador (~99,98% escrito, no cobertura del juego), dos orígenes truncados 008723/008724, 586 escenas y 2.216 cajas a verificar con naturalidad/glosario, tildes/variables, textos gráficos y prólogo pendiente. Cierre falso hasta comprobar todo en juego.
- **Gráficos G**: inventario global NO MEDIBLE; seis PNG SYS.DAT2 y 27 IMY SYSGRA analizados históricamente, 2.721 glifos originales y 19 A1–B3; TUIKA_MES.IMY CLUT2 afecta 9.144 texeles, 3.506 en zonas protegidas. Sin combate real/ROI y prueba 19 glifos multicontesto/varias tintas; `white_new_ink=False`.
- **ROMhacking R**: solo 3.724/8.248 sustituciones históricas integradas con offsets fijos (45,15% de ese conjunto), otras 4.524 longitud variable **BLOQUEADAS**. Intro demo1001 tiene 97 textos: 11 mismo tamaño simulados RAM-only, 85 variables no seguros, 1 idéntico. Modelo lineal movería 588/878 comandos; padding original 48B y déficit >=144B en tres bloques. No se han demostrado llamadas/retornos MIPS, relocalización ni release BPS/EXE final.
- **Betatesting Q**: matriz de 51 casos Q001–Q051, con Q050 y Q051 nuevos NOT_RUN; no es el universo cerrado, ninguna prueba de gameplay C en R13. Falta segundo nivel, combate, enciclopedia, guardado/carga, finales, gráficas y Windows x64 GUI E2E; 0 P0/P1 abiertos para cierre definitivo.
- **A ISO exacta**: original privado USA de 305496064 bytes, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. DATA.DAT/349 PSPFS. SCRIPT.DAT SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, SCRIPT.TBL SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. 1.625 scripts, 51.705 comandos, 46.308 no textuales. ISO intacta. NO asumir que ruta temporal persiste.

**NOVEDAD A R13 — GRAFO NUMÉRICO DE CINCO ENLACES CANDIDATOS:** `scr01.dsf` bloque20 orden20, 0x0A u32=100100 → por valor−100 ID100000/bloque**757**; desde bloque757 orden2, 0x0A u32=100200 → bloque**758**. En bloque758 orden1, 0x0C u32=100290 → bloque**759**; bloque758 orden416, 0x0A u32=100201 → bloque**760**; bloque760 orden1, 0x0C u32=100291 → bloque**761**. Con interpretación literal, el comando en bloque757 apuntaría al bloque764 de demo1002, no al contenido principal del prólogo. Esto FAVORECE ESTÁTICAMENTE la hipótesis ID+100 pero **NO prueba que exista salto en MIPS**.

**NOVEDAD GLOBAL**: para opcodes 0x0A/0x0B/0x0C los matches numéricos valor−100 de SCRIPT.TBL son **860/862, 158/166, 66/102**. Referencias con mismo nombre de fichero (origen y destino numérico): **86/860** en 0x0A, **142/158** en 0x0B, **64/66** en 0x0C. Ninguna apunta al mismo bloque del comando. Resto de operandos: 0x0A u32=0 (1) y 1 (1); 0x0B u32=3 (8); 0x0C u32=100 (36). Los bloques de intro **758 y 760** tienen cada uno 0x0C con ID candidato y otro 0x0C con argumento 100; los bloques 759 y 761 contienen un 0x0C con 100. No atribuir semántica a estos patrones sin observar ejecución.

**B R13**: herramientas `tools/f4_r13_grafo_intro.py`, `tests/test_f4_r13_grafo_intro.py`, 18 tests sintéticos PASS local. Función pura aplicada a los 51.705 comandos de la ISO original mediante parser independiente; informe privado de metadatos SHA256 `ca08137b06cdbb3a9d065a69bae7a552f3fdf393d8f567e2287f64085e7b25dd`. Informe público `reports/F4_R13_GRAFO_INTRO_2026-11-23.json`, documento `docs/F4_R13_GRAFO_INTRO_2026-11-23.md`. Verificar CI en HEAD FINAL R13, no asumir 18 PASS significan C.

**C R13**: PPSSPP oficial 1.20.4 NO EJECUTADO. AppImage ausente; `curl` a github.com falló con DNS. Original `PSP_GAME/SYSDIR/EBOOT.BIN` lleva cabecera `~PSP` y `BOOT.BIN` empieza con ceros; no permiten alegar disassembly de MIPS real. Sin PCs, capturas ni tramas nuevas.

## 2. LECTURAS Y COMANDOS OBLIGATORIOS

Leer ANTES de tocar: `AGENTS.md`, `README.md`, `CHANGELOG.md`, `docs/REPRODUCIBILIDAD.md`, `docs/PROTOCOLO_REINSERCION_FAIL_CLOSED.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md`, `docs/F4_R13_GRAFO_INTRO_2026-11-23.md`, `reports/F4_R13_GRAFO_INTRO_2026-11-23.json`, `tools/f4_r13_grafo_intro.py`, `tools/f4_r12_candidatos_especiales.py`, `tools/f4_r11_desfase_ids.py`, `tools/f4_r10_cruce_script_ai.py`, `tools/f4_r9_perfil_opcodes.py`, `tools/f3_referencias_riesgo.py`, `tools/script_event_guard.py`, `docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md`, `docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/ESTADO_CIERRE_4_AREAS.md` y este prompt.

En checkout Git real y sin perder cambios:
```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p 'test_f4_r13_grafo_intro.py' -v
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # DEBE FALLAR hasta que cuatro áreas cierren
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
```

Con ISO original SHA exacta y en ruta **PRIVADA** fuera del repositorio, no sobreescribir reporte:
```bash
python tools/f4_r13_grafo_intro.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F4_R14_GRAFO_NUEVO.json
```

Si terminal no puede clonar/fetch por DNS, usar conector GitHub para HEAD, lectura/commits NO FORZADOS, PR y workflows push/PR. No confundir CI público con pruebas de ISO.

## 3. P0 F4: PRUEBA C DE CADENA REAL, NO INFERIR CONTROL DEL GRAFO

Recuperar PPSSPP Linux x86_64 oficial v1.20.4 AppImage, hash histórico `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`; validar origen y SHA antes de ejecutar. ISO USA SHA exacto, PID/starttime, FD ISO y WebSocket 24192 del MISMO proceso; backend y captura X11 real. Si imposible, registrar bloqueo y maximizar auditoría A/B sin llamar C a los resultados.

1. **Q050:** localizar en ejecución secuencia `scr01.dsf` bloque20/orden20 offset7420, 0x0A u32=100100; observar realmente si entra a bloque757 o 758. Posteriormente observar bloque757 orden2, 0x0A u32=100200, verificar si alcanza 758 o 764; y bloque758 orden416, 0x0A u32=100201, ¿alcanza 760? Guardar PC MIPS/registros/stack/tabla/return de ejecución, no inventar RAMaddr=offset.
2. **Q051:** en bloque758, comparar 0x0C orden1 u32=100290 (candidato bloque759) con 0x0C orden415 u32=100; en bloque760, orden1 u32=100291 (candidato 761) contra orden336 u32=100. Comprobar el despacho real, estado, retorno y ruta de fin/continuación sin etiquetar centinela o salto antes de observarlo.
3. Investigar 0x0B (158 referencias numéricas de 166, valor especial 3×8, quinto byte 100/101), 0x0A casos 0/1, 0x0C restantes u32=100 en 34 bloques, referencias de 16 bits y tablas indirectas. El grafo numérico **no** es modelo completo del intérprete.
4. Solo con semántica total y referencias reales demostrar primera reubicación variable reversible en ISO PRIVADA mediante A/B/A PPSSPP; reparsear 51.705 comandos, comparar 46.308 no-textos byte exacto y 349 PSPFS ajenos sin desplazamientos. **No liberar 85 variables demo1001 ni 4.524 globales** hasta entonces; `--event-safe-only`.

## 4. P0 F3/F2 y P1 T/G/Q/F6

**F3 prólogo:** frase visible inglesa `Some say, because the treasures were there.` sigue sin fuente de letras demostrada. 231 firmas IMY ANIME000 (136 tipo00/95 tipo02) no prueban frames ni texto. Renombrar ANIME000 causó crash pre-título; no repetir. Con PPSSPP real enlazar lectura archivo/descompresión a RAM/GE/VRAM/TEXADDR/CLUT/PRIM y localizar ROI real o script; parche local reversible sin CLUT global y A/B/A.

**T:** terminar revisión contextual 9.237 filas, glosario y 586 escenas/2.216 cajas; fuente 008723/008724 truncada sin inventar texto, cajas/idioma natural/tildes/variables, sincronizar CSV, TXT y guiones sin modificar corpus original. Incluir texto visual fuera de CSV al censo.

**G:** TUIKA_MES.IMY 256×256 4bpp CLUT2 con 9.144 texeles, 3.506 protegidos; no recolor de CLUT2 global. Fuente CP932 2.721 originales +19 `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` en A1–B3, `white_new_ink=False`; verificar glifos con distintas tintas en diálogo/HUD/Opciones/batalla y TUIKA en combate A/B/A. Inventario global pendiente.

**Q:** al menos 51 casos Q001–Q051 (aún NO universo final). Ejecutar en PPSSPP C con evidencias privadas trazables y SHA, cerrar 0 P0/P1, segundo nivel, mapas/retratos/tiles/audio, inventario/enciclopedia, combate, guardar/cerrar/reabrir/cargar, finales/créditos y pruebas de regresión F1. No marcar PASS por tests B.

**F6:** solo cuando las cuatro áreas estén al 100% VERIFICADO, 0 cambios diferidos, MIPS y gráficos seguros, QA C integral: BPS diferencial con roundtrip/sha original→candidato y EXE Windows x64 UI E2E y pruebas negativas, revisar distribución legal. No publicar ISO, DATA.DAT, EBOOT, IMY, FONT, sprites, capturas, BPS con recursos comerciales ni dumps RAM/VRAM/GE; PR #7 sigue DRAFT, no merge.

## 5. ENTREGA Y SIGUIENTE RELEVO

Actualizar `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, `docs/ESTADO_CIERRE_4_AREAS.md` con historial intacto, reportes nuevos, pruebas y documentación. Entregar tabla antes/después T/G/R/Q y denominadores reales, fuente A/B/C, hashes, fallos/rollback, HEAD exacto, PR y CI push/PR de SHA final. Si no existe CI positivo, decirlo.

**AL TERMINAR, SI UNA SOLA ÁREA NO ESTÁ AL 100% REAL, REEMPLAZAR POR COMPLETO `prompts/SIGUIENTE_TAREA.md` CON NUEVO PROMPT AUTÓNOMO R15, COPIAR ESTA REGLA RECURSIVA 0 Y MOSTRAR ÍNTEGRO EL PROMPT R15 AL USUARIO.** Cuando T/G/R/Q estén verdaderamente cerradas, entregar informe final, checklist de lanzamiento y prompt de mantenimiento (no desarrollo adicional).

