# F3-R6 — presupuesto real de padding en los siete bloques demo1001 (23/11/2026)

**F3 ABIERTA; F2 ABIERTA; F4–F6 pendientes.** Este relevo no modificó ISO, SCRIPT.DAT/TBL, CSV, fuente, IMY ni gráficos; tampoco ejecutó PPSSPP. Los números siguientes proceden de **A** (ISO USA original autenticada + rellenos reales) y **B** (proyección del CSV español real previamente validado en CI); **NO** equivalen a ejecución C, direcciones MIPS, saltos o compatibilidad jugable.

## A. Relleno exacto en la ISO original

Se releyó la ISO privada suministrada por el usuario, **305.496.064 bytes** SHA256 **b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f**; DATA.DAT → PSPFS 231 SCRIPT.SDT → SCRIPT.DAT SHA256 **c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358**, SCRIPT.TBL SHA256 **f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37**.

Se determinó el final del **último comando original** de cada uno de los siete scripts, y se comprobaron en los bytes originales las colas de cero hasta el inicio del bloque siguiente (alineado a 16 bytes). El manifiesto público `reports/F3_DEMO1001_PADDING_ORIGINAL_2026-11-23.json` contiene solo offset, longitud e ID de bloque, sin copiar comandos ni cadenas comerciales. Las siete colas suman **48 bytes**; el espacio reservado a esos bloques suma **10.912 bytes**.

| ID de script | Comandos | Padding cero en original | Delta total de texto ES | ¿Cabe la concatenación hipotética en el bloque actual? | Capacidad adicional mínima por bloque si alineación 16 B |
| --- | ---: | ---: | ---: | --- | ---: |
| 100000 | 5 | 14 | 0 | Sí | 0 |
| 100100 | 422 | 11 | −1 | Sí | 0 |
| 100190 | 27 | 3 | 0 | Sí | 0 |
| 100101 | 339 | 13 | **+115** | **No** | **112** |
| 100191 | 28 | 2 | 0 | Sí | 0 |
| 100110 | 23 | 4 | **+15** | **No** | **16** |
| 100120 | 34 | 1 | **+2** | **No** | **16** |
| **Total** | **878** | **48** | **+131** | **3 bloques no caben** | **144** |

Los **144 bytes** representan la ampliación mínima de *capacidad de bloque individual* bajo una concatenación lineal y alineación 16, **NO** una predicción del crecimiento de ISO. No se ha modelado padding intermedio, llamadas, desplazamientos de script, punteros, mecanismos del intérprete ni reubicación de archivos PSPFS.

## B. Herramientas verificables y guardas

- `tools/f3_presupuesto_padding_intro.py`: utiliza el verificador previo `tools/f3_anclar_intro.py` para validar **9.237 filas reales** del borrador, **97 textos demo1001**, SHA del blob canónico y huella de procedencia `b0d42d8cd871246addf08a54e02c2a84cda52cab39f5810ef5ba2d9173e3e34e`. A continuación combina los deltas del CSV con el padding original. Con `--iso-original` revalida los finales de bloque y bytes cero de una ISO autenticada, con evidencia privada exclusivamente. Rechaza SHA, ID, ordinal, límites, capacidad o sumas inesperadas.
- `tests/test_f3_presupuesto_padding_intro.py`: **14 pruebas sintéticas locales PASS** (capacidad, 144 bytes, 588 desplazamientos previos, alteración de SHA/padding y fallos cerrados), más **1 prueba de integración** que necesita el CSV real de GitHub; no atribuirla a la sesión local sin checkout. El CI debe ejecutarla sobre la rama efectiva.
- El workflow `.github/workflows/validacion-integracion-eventos.yml` añade un paso `python tools/f3_presupuesto_padding_intro.py` usando únicamente CSV y manifiestos públicos, sin ISO ni recursos del juego.
- Informe agregado: `reports/RESULTADO_F3_R6_PRESUPUESTO_PADDING_2026-11-23.json`. Informe local privado de metadatos, sin contenido comercial, SHA256 `bb87589a99c7294e4d15201cfacd3b0e78e83ce550deeb221151338c294b0a58`.

Comandos (en checkout auténtico, copia ISO fuera de GitHub):

~~~bash
python tools/f3_presupuesto_padding_intro.py
python -m unittest discover -s tests -p 'test_f3_presupuesto_padding_intro.py' -v
python tools/f3_presupuesto_padding_intro.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/F3_R6_NUEVO.json
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
(cd patcher && go test ./...)
~~~

## Incidencia nueva y límites

En el script **100100**, el total de bytes **disminuye uno** y el bloque cabe, pero **268 comandos cambiarían su offset de inicio** si se concatenaran los textos sin preservación de posiciones; por tanto **CABER ≠ SEGURIDAD MIPS**. En total F3-R5 proyectó **588 de 878 comienzos desplazados**, separados del riesgo de ampliación de los tres bloques. Ninguno de los 588 es por sí mismo un salto roto.

**No desbloquear los 85 diálogos de longitud distinta ni los 4.524 scripts globales; conservar `--event-safe-only`, `white_new_ink=False`, 9.237 filas, 349 PSPFS y el PR #7 OPEN/DRAFT.** La procedencia de las letras inglesas del prólogo sigue sin confirmarse por GE/VRAM; los 95 IMY tipo02 de ANIME000 no tienen decodificación demostrada. En F2, CLUT2 afecta 9.144 texeles si se colorea globalmente, incluidos 3.506 en zonas protegidas: no usar esa modificación como solución de traducción. Falta aún A/B/A de TUIKA en combate, prueba de 19 caracteres y traza MIPS→RAM→GE→VRAM. F5/F6 todavía requieren validación real de juego y parche final.

**Siguiente objetivo:** PPSSPP 1.20.4 legítimo en sesión auténtica, demostrar intérprete MIPS, destino real de referencias y origen GE de letras; solo después modelar/reparar desplazamientos de comando y validar juego con A/B. Mantener regeneración recursiva de `prompts/SIGUIENTE_TAREA.md` en cada relevo.
