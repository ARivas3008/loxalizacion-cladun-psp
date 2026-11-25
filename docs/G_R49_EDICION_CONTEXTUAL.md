# G-R49 — edición contextual de 53 recursos conocidos

Se rehízo la totalidad de los 47 objetivos gráficos editados en R48, más las seis PNG históricas, **desde la ISO auténtica**, porque el paquete privado R48 y su texto exacto no pudieron recuperarse. Se aplicó el glosario canónico y el corpus revisado (blob 400a9c9ec06f7456b5ec6e11f7502d711b0a976e); cuando el texto de ese corpus contenía errores, se corrigió manualmente siguiendo contexto, autorización del usuario y consistencia lingüística. No se modificó el corpus ni el perfil ROMhacking.

## Prólogo
ANIME000.IDT IMY192 registro 188 256×128: se leyó el raster original de ocho líneas y se reescribieron como oraciones continuas; sin punto por renglón. Misma narración final en PIC0.PNG. Texto:
> Unos dicen que por los tesoros que allí había,
>
> otros, porque allí hay que vencer al enemigo,
>
> y otros, porque allí se forjan los sueños.
>
> Ese «allí» puede estar al fondo de un pozo
>
> o incluso tras la puerta de un baño público.
>
> Cualquiera puede llegar a ese lugar,
>
> pero está conectado con muchos otros lugares.
>
> A ese mundo lo llaman «Arcanus Cella».
Se probaron 12 alternativas tipográficas; elegida Noto Serif Condensed Bold 11 px por legibilidad y ajuste. Recompresión IMY hasta 4306 B +2 de cola original; 4308 B exactos, no desplazamiento. Copia ISO diagnóstica de 305496064 B, 4212 bytes distintos exclusivamente en el slot absoluto 120574224, 230 IMY IDT y 348 PSPFS ajenos idénticos. No es una ISO acumulada ni evidencia de ejecución. La paleta externa del prólogo no está demostrada en runtime.

## Ediciones
1 prólogo, 34 superficies de créditos (17 pares exactos, nombres preservados, 208/226 solo nombres intactos), 5 SYSGRA (24 etiquetas), 4 animaciones (HELP, AMPL., RUPTURA con fases), TITLE_LOGO.MPB, ICON0.PNG, PIC0.PNG, 6 PNG históricas. 53/53 guardas de píxeles fuera de ROI, roundtrips de cada códec, y **53/53 SHA comprimidos exactos en reproducción independiente y repetición desde ZIP**. 141498 píxeles editados, 36 recursos crecen, 16 disminuyen, 1 igual. LVSP preservado por glosario. Correcciones editoriales explícitas: Maná y Correr aun cuando campos 005349/005354/005667 del CSV dicen Dónde/Ejecutar; HP conforme al glosario; Guardia de ángel conforme a contexto. Abreviaturas de UI (Cualq., ¡NVO!, AMPL., Sin ataque esp.) por anchura; validar en juego. Las seis PNG son nuevas variantes, no afirmamos identidad con los binarios R48 previos. Fuentes alternativas no son las fuentes originales; validar estilo y legibilidad final.

Paquete privado `Cladun_ES_G_R49_edicion_contextual_PRIVADO.zip` incluye 53 deltas de imágenes, XOR extra del flujo comprimido de prólogo, 99 ficheros, previews, hashes y herramienta `reproducir_r49.py`; no ISO ni fuentes ni originales completos. SHA y hashes en `reports/G_R49_EDICION_CONTEXTUAL.json`. **No subirlo al repo**. Ejecutar en carpeta privada:
```bash
python reproducir_r49.py --iso /PRIVADO/USA.iso --report /PRIVADO/REPLAY_R49.json
python tools/g_r49_prologo_reinsercion.py --package /PRIVADO/Cladun_ES_G_R49_edicion_contextual_PRIVADO.zip --iso /PRIVADO/USA.iso --candidate /PRIVADO/R49_INTRO_DIAGNOSTICO.iso
```
El último comando genera exclusivamente la variante diagnóstica del prólogo, exige hash de ISO original y de candidata. No aplicar ese offset absoluto a una ISO reconstruida.

**100% del conjunto conocido de ediciones (53/53), NO 100% del universo gráfico del juego.** 309 superficies de paleta/escena, 4 condicionales, 2 abreviaturas y 7 fuentes pendientes, 36 flujos crecen y necesitan reconstrucción de contenedor. Sin PPSSPP, sin ISO acumulada de los 53, sin release. El PR queda DRAFT.
