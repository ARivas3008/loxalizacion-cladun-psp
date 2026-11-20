# Uso de la referencia terminológica de La Pucelle en Cladun

**Alcance:** consulta editorial para la rama `revision-manual-dialogos`. Se conserva el glosario propio de Cladun en `traduccion/GLOSARIO_CANONICO.csv` sin sobreescritura.

## Origen verificable

La tabla `referencias/la_pucelle/terminos_investigados.csv` es una copia documental del fichero público `glosario/terminos_investigados.csv` de [La Pucelle: Ragnarok](https://github.com/ARivas3008/la-pucelle-ragnarok-localizacion/blob/main/glosario/terminos_investigados.csv), propiedad del mismo proyecto de localización del usuario. Contiene 36 términos: originales japoneses, traducción de trabajo, equivalente inglés, grado de confianza, fuente externa y nota. Un elemento figura `Sin resolver`. No es una base SQLite ni un diccionario general del español.

La comparación con los 67 términos propios de Cladun encontró **cero coincidencias exactas** entre original/equivalente inglés y entradas originales del glosario. Por tanto, **cero términos se han importado automáticamente al glosario canónico de Cladun**. La coincidencia futura tampoco bastaría para copiar la traducción: se examinará escena, sentido y mecánica.

## Principios reutilizables, tomados de casos concretos

1. **Nombres propios y tratamiento.** La Pucelle conserva *Prier*, *Alouette*, *Culotte* y *Éclair* tras comprobar la denominación; Cladun debe conservar sus propios *Pudding*, *New-geon*, *Arcanus Cella*, etc. Nunca trasladar nombres entre juegos.
2. **Mecánicas aparentemente similares.** La Pucelle distingue *Portal oscuro* (objeto purificable) de *Puerta al Mundo Oscuro* (acceso). Aplicar el mismo principio a Cladun: *Job* puede ser clase en menús y trabajo en un diálogo; *Widen* no significa lo mismo que *Widening*. La correspondencia exacta requiere contexto.
3. **Voz narrativa.** Consultar diálogo anterior/siguiente y la identidad verificable del hablante. Mantener un tratamiento coherente (tú/usted) según personaje y relación, evitar calcos y respetar humor, interjecciones y juego de palabras. Ninguna frase se declara revisada únicamente por consultar esta tabla.
4. **Cadenas dañadas.** La Pucelle conserva `ェD` como `[SIN RESOLVER]`; en Cladun, los campos truncados o sin atribución tampoco deben reconstruirse por intuición.
5. **Ancho de pantalla y controles.** La ficha *Re-Action* pide comprobar interfaz y ancho de caja antes de traducir. Revisar en Cladun caracteres acentuados, tamaño de glifos, saltos y `%s`/`%d`/marcadores; que el CSV esté bien no demuestra que PPSSPP renderice bien.
6. **Fidelidad.** Evitar traducción automática literal sin cotejar inglés y japonés cuando estén disponibles. No modificar offsets, recursos gráficos ni scripts desde esta revisión editorial.

## Ejemplo aplicado a la captura aportada

- CSV previsto: **«Joven frenético»**. En pantalla aparece «Joven frené tico». **Clasificación: error tipográfico de render/avance de glifo**, no una razón para quitar la tilde.
- Texto en pantalla: «No te vayas así, sin más». Revisar naturalidad de cada intervención en contexto, puntuación y segmentación, pero **no** cambiar una frase solo para disimular errores de la fuente.
- El guion con nombres en `lectura/CLADUN_GUION_CON_HABLANTES_ES.txt` es una ayuda, no una identificación perfecta de quién habla.

## Procedimiento de cotejo

Ejecutar desde la raíz de la rama:

    python tools/auditar_referencia_la_pucelle.py
    python -m unittest tests.test_referencia_la_pucelle -v

El informe generado `reports/auditoria_referencia_la_pucelle.json` muestra coincidencias exactas y posibles desacuerdos. Las coincidencias son **alertas de revisión humana**, no reemplazos. Después, corregir solo la columna `espanol` del CSV mediante el editor existente; utilizar el importador con validación y probar en PPSSPP las cadenas modificadas.

**No se editó el corpus, el glosario de Cladun, el parche ni la ISO.**
