# SIGUIENTE TAREA — Cladun ES / continuar F1 hasta demostrar reparación en PPSSPP

Actúa como especialista senior en ingeniería inversa de PSP, sistemas de scripts, localización española, parches BPS y pruebas reales en PPSSPP. Tu objetivo es **continuar la implementación**, no redactar planes hipotéticos. Realiza las modificaciones y pruebas efectivamente posibles, aporta hashes, capturas genuinas y commits verificables. NO declares corregido un fallo únicamente porque pasó la auditoría estática.

## 1. Repositorio y punto de partida

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp

Rama de trabajo y PR abierto de tipo borrador:
- integracion-eventos-segura-20261120
- https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
- Base del PR: revision-manual-dialogos

Lee ANTES de editar:
- AGENTS.md
- README.md
- docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md
- docs/AUDITORIA_MENU_TILDES_SIMBOLOS_2026-11-20.md
- docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md
- docs/EXPERIMENTO_MENU_F1_2026-11-20.md
- reports/menu_f1_metricas_original_2026-11-20.json
- reports/ESTADO_CONTINUIDAD_PPSSPP.json
- prompts/PROMPT_INICIAL_CORRECCION_PPSSPP.md
- tools/experimento_menu_f1.py
- tests/test_experimento_menu_f1.py
- tools/integrar_parche_seguro.py
- tools/generar_parche_bps.py
- tests/test_script_event_guard.py

Nunca sobrescribas el corpus y el borrador canónicos sin motivo probado; usa nuevas salidas para cada variante. No subir ISO, PBP, BPS, datos del juego, fuentes, PNG comerciales, EXE con payload ni capturas con activos comerciales al GitHub público.

## 2. Progreso confirmado y archivos cambiados en la última etapa

**F1 todavía NO está resuelta.** El estado previo de PPSSPP 1.20.4 Linux mostraba caja de Opciones aproximada de 764 px con ISO USA y 333 px con v0.1.5, solapamiento de valores, y parte de la introducción aún en inglés. Esas capturas se conservaron en un ZIP privado anterior; NO son evidencia nueva ni se dispone de ellas dentro del repositorio.

La nueva etapa verificó la ISO USA original del archivo adjunto en la conversación, 305.496.064 bytes y SHA-256:
b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f

Su recurso DATA.DAT contiene 349 PSPFS. DATABASE.DAT (index 193) se descomprimió; STRTBL.DAT tiene 17.744 bytes, SHA:
16d9da36c05380cbb8af7eba53cb26c7b3e21f8ef5c80fdb90fdba20621044bf

FONT.BIN de FONT.ARC (index 308) tiene 2.721 registros de origen, SHA:
1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46

Medidas desde FONT.BIN original (ancho original → español v0.1.5 → variante propuesta):
- 005695 Retro: 85 → 33 → 85 px (restituir sangría ideográfica).
- 005696 Real: 83 → 59 → 83 px (restituir sangría ideográfica).
- 005697 %2d: 99 → 22 → 99 px (restituir exactamente diez espacios anteriores y uno posterior).
- 005698 Correr: 170 → 106 → 170 px (relleno final ajustado).
- 005709 Decimales de daño: 303 → 111 → 303 px (relleno final ajustado).
- 005713 APAGADO: 84 → 115 px, SIN modificar por ahora; necesita inspección de alineación y contexto.

Los avances anteriores son estimaciones FONT.BIN, no dimensiones PPSSPP. La causa de compresión de la ventana NO está probada. La hipótesis es cálculo dinámico de ancho a partir de los textos y espacios; también cabe conflicto con el atlas/índices/rutina de ventanas.

Cambios efectivamente subidos:
- tools/experimento_menu_f1.py — lectura de métricas desde ISO con comprobación SHA, generación de variantes CSV separadas y reporte JSON; solo cinco IDs autorizados; protege el marcador %2d.
- tests/test_experimento_menu_f1.py — pruebas unitarias de prefijos, sufijos, ancho, rechazos y variable de formato.
- reports/menu_f1_metricas_original_2026-11-20.json — evidencia estática de ISO original, hashes y métricas.
- docs/EXPERIMENTO_MENU_F1_2026-11-20.md — protocolo con comandos para ensayos individuales/conjuntos, PPSSPP y criterios de salida.
- README.md — resumen del estado real sin afirmar corrección de menú.
- reports/ESTADO_CONTINUIDAD_PPSSPP.json — consulta el estado actualizado de incidencias.
- prompts/SIGUIENTE_TAREA.md — este relevo autónomo.

GitHub Actions ejecución 44861999891, commit a75bcb34954cc38483977e7550f8d40ea1305b5e: SUCCESS. Se ejecutaron 120 pruebas Python, integridad de fuente/borrador, planificación, Go test y build público Windows sin payload. **No se ejecutó PPSSPP ni el integrador/BPS con la ISO privada en CI**. No se fabricaron capturas.

Hashes de la versión anterior, únicamente como referencia histórica:
- ISO v0.1.5: 9be7b07a2c5c8c9026ffd0f829f613237f9a31e8fe2455856649ff6c1fe2b4ef
- BPS v0.1.5: 976fda78adf3e6c2c3c31d5b89bc2f04b18c0905789305b25e9d0a58bf8cea0c
No existe aún candidato v0.1.6 ni nuevos hashes que puedan sustituirlos.

## 3. TAREA INMEDIATA: F1, experimentos mínimos en PPSSPP

1. Comprueba que cuentas con la ISO exacta (estaba en /mnt/data/cladun_privado/Cladun_USA_original.iso cuando se ejecutó la etapa anterior; si no está montada, descomprime el 7z privado adjunto y coteja SHA). Nunca la subas a GitHub.
2. Obtén checkout de la rama correcta. Si existe un worktree local, úsalo en vez de clonar innecesariamente. No reemplaces avances anteriores.
3. Ejecuta el script F1 con --ids 005697 y después 005709 en **dos CSV distintos**. Luego crea variante de todos los cinco IDs. Comprueba en cada informe que los anchos propuestos igualan al original y que solo se cambió el campo español de esos IDs, sin reordenar registros ni modificar originales, offsets, IDs o bytes_hex.
4. Para cada CSV usa tools/integrar_parche_seguro.py con --borrador y OBLIGATORIAMENTE --experimental-parcial --event-safe-only, salida privada distinta y JSON de integración. Si bloquea, analiza por qué, corrige la causa y NO desactives el modo seguro.
5. Genera BPS experimental por cada ISO candidata y comprueba su reconstrucción exacta, SHA, inventario ISO9660, 349 recursos PSPFS, miembros DSARC ajenos, fuentes y 51.705 comandos originales. No consideres aprobada la prueba si se alteran 46.308 opcodes no textuales o offsets de 1.625 scripts.
6. Ejecuta en PPSSPP 1.20.4 preferentemente a resolución/ventana iguales al control anterior: ISO USA, v0.1.5, solo 005697, solo 005709 y versión conjunta. Registra versión y backend gráfico; captura el menú de configuración con igual encuadre, dos posiciones del cursor, opciones de volumen, Tipo música, Controles y Decimales de daño. Mide ancho real de caja, cortes de texto, superposiciones, alineación, símbolos de botones y signos. Capturas auténticas o bloqueo explícito.
7. Si la variante 005709 por sí sola devuelve la anchura normal y no genera regresiones, diagnostica si la rutina mide el texto; si se conserva el fallo, prueba fuente sola, DATABASE sola, SYS.DAT2 solo y combinaciones con aislamiento de recursos, luego inspecciona desensamblado de la rutina de tamaño de ventana. Nunca atribuyas la causa sin pruebas reproducibles.
8. No cambies 005713 por ensayo arbitrario ni borres tildes/¿¡ para hacer encajar la caja. Solo después de pruebas visuales acepta una variante mínima y registra la corrección exacta en el borrador canónico, sus TXT sincronizados y un CSV antes/después según AGENTS.md.

## 4. Comandos reproducibles

~~~bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-f1-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-f1-integrabilidad.json
(cd patcher && go test ./...)
git diff --check

export ISO_ORIGINAL='/ruta/privada/Cladun_USA_original.iso'
sha256sum "$ISO_ORIGINAL"
mkdir -p /tmp/cladun-f1/{csv,reportes,iso,bps}

python tools/experimento_menu_f1.py \
  --iso "$ISO_ORIGINAL" \
  --salida-csv /tmp/cladun-f1/csv/solo-005697.csv \
  --reporte /tmp/cladun-f1/reportes/solo-005697.json --ids 005697

python tools/experimento_menu_f1.py \
  --iso "$ISO_ORIGINAL" \
  --salida-csv /tmp/cladun-f1/csv/solo-005709.csv \
  --reporte /tmp/cladun-f1/reportes/solo-005709.json --ids 005709

python tools/experimento_menu_f1.py \
  --iso "$ISO_ORIGINAL" \
  --salida-csv /tmp/cladun-f1/csv/los-cinco.csv \
  --reporte /tmp/cladun-f1/reportes/los-cinco.json

NOMBRE='solo-005709'
python tools/integrar_parche_seguro.py \
  --iso "$ISO_ORIGINAL" \
  --borrador "/tmp/cladun-f1/csv/$NOMBRE.csv" \
  --candidate "/tmp/cladun-f1/iso/$NOMBRE.iso" \
  --report "/tmp/cladun-f1/reportes/$NOMBRE-integracion.json" \
  --experimental-parcial --event-safe-only

python tools/generar_parche_bps.py \
  --original "$ISO_ORIGINAL" \
  --candidato "/tmp/cladun-f1/iso/$NOMBRE.iso" \
  --informe-integracion "/tmp/cladun-f1/reportes/$NOMBRE-integracion.json" \
  --salida "/tmp/cladun-f1/bps/$NOMBRE-EXPERIMENTAL.bps" \
  --informe-bps "/tmp/cladun-f1/reportes/$NOMBRE-bps.json" \
  --experimental --event-safe-only

sha256sum "$ISO_ORIGINAL" "/tmp/cladun-f1/iso/$NOMBRE.iso" \
  "/tmp/cladun-f1/bps/$NOMBRE-EXPERIMENTAL.bps"
~~~

Repetir el tramo de integración/BPS variando NOMBRE para solo-005697 y los-cinco. Las salidas no deben existir antes de cada ejecución. Si se necesita comparar solo la fuente, --sin-fuente NO valida acentos y nunca sirve como parche final.

Comprobación Windows pública sin BPS ni payload:
~~~bash
cd patcher
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 \
  go build -trimpath -ldflags='-H=windowsgui -s -w' \
  -o /tmp/cladun-interfaz-sin-payload.exe ./cmd/cladun-patcher
~~~

## 5. Criterios de aceptación, bloqueos y fases posteriores

**No cerrar F1 hasta:** una variante concreta con causalidad aislada y capturas PPSSPP reales comparables; anchura de ventana y texto legibles sin superposición; tildes, iconos y ayudas bien representados; hashes nuevos y verificación de roundtrip BPS; 349 PSPFS y resto ISO9660 inmutables fuera de recursos textuales previstos; cero alteraciones de instrucciones y offsets; test Python/Go en verde; registro de antes/después y actualización de README/estado/PR. Si falta una sola evidencia, documentar F1 como bloqueada y repetir experimento específico en el relevo.

Después de F1:
- F2: símbolos de botones, índices físicos del atlas FONT.BIN, 19 glifos A1–B3, ¿¡/acentos, renders PPSSPP.
- F3: identificar el origen exacto de las frases aún inglesas de introducción y corregirlas sin alterar eventos.
- F4: explicar y demostrar referencias internas del intérprete antes de integrar las 4.524 traducciones aplazadas. **Nunca retirar --event-safe-only sin prueba de referencias.**
- F5: recorrer transiciones, mapa, segundo nivel, combate, enciclopedia, equipo y guardado/carga con comprobaciones repetibles.
- F6: BPS y EXE privado Windows x64 con hashes nuevos, sin distribuir assets del juego.

## 6. ENTREGA OBLIGATORIA Y RELEVO RECURSIVO

En tu respuesta distingue claramente: verificado binariamente, comprobado visualmente, probado funcionalmente y pendiente. Reporta comandos ejecutados, logs Python/Go, hashes de todas las ISOs y BPS realmente creados, recursos y eventos preservados, capturas reales, URLs de PR/commits y bloqueo principal. No inventes archivos, capturas ni SHA.

**AL TERMINAR ESTA TAREA DEBES OBLIGATORIAMENTE CREAR UN NUEVO PROMPT AUTÓNOMO** y guardarlo en **prompts/SIGUIENTE_TAREA.md** (sustituyendo este), además de mostrar su texto completo al usuario. Debe incluir los archivos modificados, causas demostradas y descartadas, comprobaciones, comandos, hashes, estado de incidencias y la siguiente tarea concreta. **Ese nuevo prompt DEBE exigir a su vez generar otro prompt actualizado al finalizar.** Esta obligación es recursiva en cada fase, incluso si la fase actual sigue bloqueada. Actualiza también reports/ESTADO_CONTINUIDAD_PPSSPP.json y deja commits en la misma rama y PR #7 sin fusionar una versión no certificada.
