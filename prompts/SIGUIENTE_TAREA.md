# NUEVA TAREA CLADUN ES — F1: terminar ancho exacto, valores ON/OFF y comprobación PPSSPP

Actúa como especialista senior PSP, ingeniería inversa, fuentes, localización, seguridad de eventos, BPS y PPSSPP. Tu tarea es ejecutar cambios y pruebas reales, actualizar GitHub y entregar evidencias verificables. No te limites a escribir instrucciones ni declares completado nada que no tenga pruebas.

## Repositorio y lectura inicial
- GitHub: https://github.com/ARivas3008/loxalizacion-cladun-psp
- Rama: integracion-eventos-segura-20261120
- PR borrador #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
- Base PR: revision-manual-dialogos
- Lee AGENTS.md, README.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/RESULTADO_F1_PPSSPP_2026-11-20.md, docs/EXPERIMENTO_MENU_F1_2026-11-20.md, reports/RESULTADOS_F1_PPSSPP_REAL_2026-11-20.json, reports/ESTADO_CONTINUIDAD_PPSSPP.json, tools/menu_layout_es.py, tools/integrar_parche_seguro.py, tools/experimento_menu_f1.py, tests/test_menu_layout_es.py y tools/generar_parche_bps.py.

## Evidencia y archivos de la fase anterior
Se ejecutó PPSSPP REAL 1.20.4 Linux en software renderer / Xvfb 1280×720 y ventana 960×544. El AppImage oficial tiene SHA-256 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21. Se sustituyó SDL_AUDIODRIVER=pulseaudio por dummy en la configuración local extraída, sin alterar el emulador. Teclas probadas: Return para entrar al título, Down para Opciones, z para confirmar. Las capturas reales están en ZIP privado Cladun_F1_capturas_reales_PPSSPP_2026-11-20.zip (SHA-256 4d7f83259dcfe37242700c6cce1dbbee9e36945c1860d5e9fff9a30c7b58cae2). No están ni deben subirse a GitHub.

La ventana se midió en capturas reales con segmento horizontal claro de y=106, umbral RGB>125 y x=160..1104:
- ISO USA original: x342..1097 = 756 px interiores / ~764 exteriores.
- v0.1.5 reproducida exactamente: x774..1097 = 324 interiores / ~332 exteriores; superposición.
- Solo cambio 005697: 324 interiores / ~332 exteriores, control negativo.
- Solo cambio 005709: x358..1097 = 740 interiores / ~748 exteriores; sin solapes en pantalla principal, cursor y ayudas probados; se abrió Controles.
- Cinco cambios de espacio: 740 / ~748, idéntico a solo 005709.

CAUSA DEMOSTRADA para el defecto principal: al traducir 005709 en DATABASE.DAT/STRTBL.DAT se suprimió el relleno final de espacios ideográficos y disminuyó el ancho que calcula el motor. La solución mínima versionada restaura relleno SOLO en esa cadena, con fail-closed por bytes/ID/original. tools/menu_layout_es.py devuelve el texto de presentación "Decimales de daño" + diez espacios ideográficos + seis ASCII, sin modificar el CSV ni TXT literarios; tools/integrar_parche_seguro.py lo aplica SOLO a fuente y borrador canónicos. **Si se proporciona --borrador alternativo, NO se aplica automáticamente**, por lo que un experimento con 005710 debe incorporar el relleno correcto 005709 explícitamente para no reintroducir la ventana estrecha. tests/test_menu_layout_es.py comprueba ese contrato. Otros archivos creados/actualizados: reports/menu_f1_metricas_subconjunto_2026-11-20.json, reports/RESULTADOS_F1_PPSSPP_REAL_2026-11-20.json, docs/RESULTADO_F1_PPSSPP_2026-11-20.md, README.md y reports/ESTADO_CONTINUIDAD_PPSSPP.json.

Hashes SHA-256 exactos:
- ISO original USA: b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f (305496064 bytes).
- ISO v0.1.5 antigua, REPRODUCIDA byte idéntica: 9be7b07a2c5c8c9026ffd0f829f613237f9a31e8fe2455856649ff6c1fe2b4ef.
- ISO experimental F1 v016 desde integrador canónico ACTUAL: 9b7fc809bb106953a91d6ad6e4e23363eb7fb92760659607d484f71132b5da89.
- BPS experimental F1 v016: 5047fa7b565f84ec204f7f1dde4e47752eb2013af8daa40d68714ca7255b1566.
- STRTBL.DAT original: 16d9da36c05380cbb8af7eba53cb26c7b3e21f8ef5c80fdb90fdba20621044bf.
- FONT.BIN original: 1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46.

El integrador actual reconstruye la ISO y BPS F1 CANÓNICOS idénticos byte a byte a solo 005709, la variante con QA PPSSPP. El BPS tiene roundtrip exacto; 349 entradas PSPFS, 345 recursos ajenos a cuatro contenedores de texto, recursos ISO9660 ajenos intactos; 51.705 comandos y 46.308 no textuales intactos; 1.625 inicios de scripts, 0 offsets desplazados, 4.524 sustituciones de script aplazadas con --event-safe-only. Esto es integridad estática, NO prueba de toda la aventura. GitHub Actions run 44864818033: 126 tests Python, tests Go, integridad corpus/borrador, integrabilidad y build Windows SIN payload aprobados.

Una variante adicional de 005709 con UN espacio ideográfico EXTRA se construyó y pasó seguridad binaria, pero no produjo captura utilizable de PPSSPP en esa ejecución. SHA ISO f97fa355fce8d7ab55a81fc711e944185ebdce4a320a5077695cb445acd303c8 y BPS 279bd99d7a0cfb87fd1bb4a03ee67ecc250d51563e14f12e213283922a8634fc. No la declares visualmente probada ni la adoptes sin nueva prueba.

## Tu tarea inmediata de F1
1. Coteja el residuo de 16 px entre F1 (~748 exteriores) y original (~764). **Prueba de nuevo la variante +1 espacio en PPSSPP real** con las mismas coordenadas de imagen, seleccionando Opciones tras iniciar el juego. Verifica que la mayor anchura no provoque recortes, cursor erróneo ni cambios en ayudas; mide y toma PNG auténticos. Si no da 764 o introduce regresión, conserva la corrección mínima ya adoptada e investiga el redondeo en la rutina de ventanas.
2. Examina el ID 005710: original "          ON", borrador "          EN", que debe corregirse a español natural, cotejándolo con 005713 original "         OFF" / borrador "         APAGADO", y los 005711–005712. Ensaya alternativas aisladas para ON/OFF preservando anclaje, símbolos y márgenes. Cualquier modificación literaria del CSV canónico exige sincronizar ambos TXT, bitácora antes/después y demás vistas derivadas en el MISMO COMMIT. Relleno invisible preferentemente en override separado.
3. Prueba realmente todas las posiciones del cursor de Opciones, volumen, Real/Retro, daño decimal, efectos círculo, Capturas y Controles, incluidos cambios de valor y regreso al menú. Captura al menos dos estados por pantalla. Inspecciona iconos L/R, cuadrado, círculo, cruz y triángulo, pero no declares F2 resuelta sin demostrar acceso por código versus índice del atlas.
4. Tras cambios, crea nueva ISO/BPS PRIVADOS, calcula SHA-256 y reconstrucción BPS, audita 349 PSPFS, DSARC, ISO9660, y verifica de nuevo los 51.705 comandos y 1.625 scripts sin desplazamientos. NUNCA retirar --event-safe-only por comodidad. Si una prueba falla, deja F1 explícitamente abierta con bloqueo y experimento replicable.

## Comandos verificables

~~~bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f1-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f1-integrabilidad.json
(cd patcher && go test ./...)
git diff --check

export ISO_ORIGINAL='/ruta/privada/Cladun_USA_original.iso'
export SALIDA='/ruta/privada/f1-siguiente'
mkdir -p "$SALIDA"
sha256sum "$ISO_ORIGINAL"
python tools/integrar_parche_seguro.py --iso "$ISO_ORIGINAL" \
  --candidate "$SALIDA/candidata.iso" --report "$SALIDA/integracion.json" \
  --experimental-parcial --event-safe-only
python tools/generar_parche_bps.py --original "$ISO_ORIGINAL" \
  --candidato "$SALIDA/candidata.iso" \
  --informe-integracion "$SALIDA/integracion.json" \
  --salida "$SALIDA/experimental.bps" --informe-bps "$SALIDA/bps.json" \
  --experimental --event-safe-only
sha256sum "$ISO_ORIGINAL" "$SALIDA/candidata.iso" "$SALIDA/experimental.bps"
~~~

Usar siempre archivos de salida inexistentes. Para ensayar +1 espacio crea un CSV separado a partir del borrador maestro, sustituyendo SOLO 005709.espanol por "Decimales de daño" + 10 espacios ideográficos + 6 ASCII + 1 ideográfico. Usa --borrador para ese CSV, --experimental-parcial y --event-safe-only. Espera SHA ISO f97fa355...303c8, si difiere detente y audita. No subir ISO, BPS, datos, fuentes o capturas comerciales a GitHub.

## Después de F1
F2: 19 glifos A1-B3, atlas desplazado +19 y símbolos de controles, tildes, ¿¡ y referencias internas; F3: textos en inglés de la introducción, identificar IDs/recurso; F4: modelo de referencias del intérprete para integrar las 4.524 traducciones pospuestas sin alterar eventos; F5: niveles, combate, enciclopedia, retratos, inventario, guardado/carga y regresiones; F6: BPS final, EXE privado Windows y QA completa. No confundir fases ni iniciar la siguiente mientras F1 siga bloqueada sin documentarlo.

## ENTREGA Y RELEVO RECURSIVO OBLIGATORIOS
En cada mensaje de cierre identifica avances verdaderamente realizados, causas demostradas, archivos, SHA, logs Python/Go, evidencias PPSSPP REALES, binario versus visual versus funcional, cambios en GitHub, commits, rama y PR #7. No declarar final por QA estática. Actualiza reports/ESTADO_CONTINUIDAD_PPSSPP.json con cada incidencia y sus pruebas, y **GENERA OBLIGATORIAMENTE OTRO PROMPT COMPLETO Y AUTÓNOMO EN prompts/SIGUIENTE_TAREA.md y muéstralo al usuario**. El nuevo prompt debe incluir todos los cambios, comandos, hashes, capturas y bloqueo concreto o siguiente fase; **DEBE EXIGIR A SU VEZ generar otro prompt al finalizar**. Repetir esta obligación hasta completar la traducción y la implementación total.
