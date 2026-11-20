# CLADUN: This Is an RPG! — Localización al español (PSP)

> **20/11/2026 — parcheador ISO única en prueba privada:** la interfaz de Windows ya no solicita un archivo `.bps`, solo una ISO original USA. Se ha reconstruido una **ISO candidata experimental** con las 9.237 entradas modeladas y un BPS diferencial con comprobación completa del SHA-256 final. **No hay validación de arranque ni juego en PPSSPP**, por lo que la traducción no está aprobada para distribución final. El código público de la interfaz está en [`patcher/`](patcher/README.md); el `.exe` experimental integrado y el BPS de prueba se mantienen fuera del repositorio. El antiguo `.exe` v0.1.0, que requería BPS externo, está obsoleto.

> **Estado:** fuente íntegra de 9.237 textos, borrador español de 9.235 entradas (**474 posteditadas o normalizadas por IA; 8.761 todavía automáticas**). La integración tiene **una ruta técnica estática para las 9.237 unidades**, con fuente y gráficos españoles experimentales; **todavía NO se ha validado su ejecución en PPSSPP ni se ha publicado un parche jugable**.

Proyecto de localización de la **edición USA para PSP**. Su objetivo es recuperar, ordenar y revisar **solo contenido textual traducible**: diálogos, elecciones, nombres y descripciones de objetos, personajes, monstruos, habilidades, lugares, menús, avisos, créditos y rótulos presentes en imágenes. **No se publica un listado de instrucciones internas del motor.**

## Entrar al corpus

| Archivo | Para qué sirve |
| --- | --- |
| **[`corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt`](corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt)** | **Único TXT maestro: lectura total numerada, sin traducciones.** |
| [`corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv`](corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv) | **Fuente maestra para edición**: IDs estables, texto original, español vacío, procedencia, orden, bytes. |
| [`corpus/confirmados_formato.csv`](corpus/confirmados_formato.csv) | Registros recuperados de estructuras conocidas y seis rótulos gráficos verificados. **Formato confirmado ≠ aparición en pantalla comprobada.** |
| [`corpus/revisar_visibilidad.csv`](corpus/revisar_visibilidad.csv) | Registros textuales estructurales cuyo uso visual o decodificación aún debe comprobarse. |
| [`qa/decisiones_auditoria.csv`](qa/decisiones_auditoria.csv) | Trazabilidad de correcciones, descartes y cadenas recuperadas frente a la extracción anterior. |

### Estado cuantificado

| Indicador | Resultado |
| --- | ---: |
| **Unidades textuales conservadas** | **9.237** |
| Extraídas de estructuras y rótulos identificados | 8.202 |
| Texto de campo real; uso en pantalla pendiente | 1.033 |
| Texto con dos campos CP932 incompletos | 2 |
| Nuevas unidades recuperadas en la revisión | 127 |
| Asociaciones de texto/offset corregidas | 133 |
| Referencias gráficos-textuales verificadas e incluidas | 6 |
| Traducciones finales validadas para reinserción | **0** |
| Entradas con borrador español independiente | **9.235** |

**Qué significan las cifras:** son *unidades en fuentes del juego*, no frases únicas y **no equivalen a una cobertura del 100 %**. Las cadenas repetidas se mantienen cuando ocupan posiciones distintas. Los campos marcados como pendientes se conservan en el corpus total porque podrían requerir localización, pero todavía **no están aprobados para inserción**.

### Orden e integridad

Cada grupo corresponde a un elemento textual identificable de la extracción. Se conserva su **ID, archivo de origen, registro, script/orden y offset** cuando aplica. El orden es el orden del contenido **por recurso en la edición analizada**, no necesariamente el orden en que se vive la historia. Las cadenas en inglés y japonés aparecen en su idioma original. No se corrigen, resumen ni traducen en esta fase.


## Traducción automática española y cotejo — 18/11/2026

Se conservaron los 9.237 IDs y originales, y se generó un **borrador separado**, sin sobrescribir el corpus fuente. Incluye 9.235 entradas con texto español; dos campos con bytes CP932 incompletos siguen pendientes. La primera fase tuvo 67 entradas posteditadas; el acumulado actual de revisiones y normalizaciones por IA es **474**. Otras **8.761** entradas siguen sin revisión narrativa individual.

| Material | Archivo |
| --- | --- |
| Guion original estilo FAQ (extracción anterior) | [`corpus/LECTURA_ORIGINAL_ESTILO_FAQ.txt`](corpus/LECTURA_ORIGINAL_ESTILO_FAQ.txt) |
| Texto español continuo, borrador | [`traduccion/CLADUN_BORRADOR_ES.txt`](traduccion/CLADUN_BORRADOR_ES.txt) |
| Lectura bilingüe y cotejo | [`traduccion/CLADUN_BORRADOR_BILINGUE_FAQ.txt`](traduccion/CLADUN_BORRADOR_BILINGUE_FAQ.txt) |
| CSV bilingüe con metadatos originales | [`traduccion/CLADUN_BORRADOR_ES.csv`](traduccion/CLADUN_BORRADOR_ES.csv) |
| Incidencias de QA | [`traduccion/INCIDENCIAS_QA.csv`](traduccion/INCIDENCIAS_QA.csv) |
| **Glosario canónico CSV, 67 términos** | [`traduccion/GLOSARIO_CANONICO.csv`](traduccion/GLOSARIO_CANONICO.csv) |
| Glosario anterior (archivo histórico) | [`traduccion/GLOSARIO_PROPUESTA.csv`](traduccion/GLOSARIO_PROPUESTA.csv) |
| Informe técnico y lingüístico | [`docs/INFORME_TRADUCCION_2026-11-18.md`](docs/INFORME_TRADUCCION_2026-11-18.md) |

**Aviso:** existe un códec PUA y una fuente experimental para 19 signos españoles, pero todavía faltan validar su lectura en el motor y su representación visual en PPSSPP. Ninguna traducción está aprobada para insertar todavía.


## Fase de revisión, codificación y seguridad binaria — 18/11/2026

- **Glosario canónico:** [`docs/GLOSARIO_CANONICO.md`](docs/GLOSARIO_CANONICO.md). En una fase anterior se corrigieron 130 entradas adicionales, incluyendo Pudding, Widen, personajes de apoyo, bastones y cambio de clase. Las revisiones posteriores se documentan por separado y el resto sigue sin revisión narrativa individual.
- **Análisis técnico y riesgos:** [`docs/SEGURIDAD_BINARIA_Y_TIPOGRAFIA.md`](docs/SEGURIDAD_BINARIA_Y_TIPOGRAFIA.md).
- **Codificación reversible de prueba:** [`tools/charset_es.py`](tools/charset_es.py), con 19 caracteres a códigos CP932 PUA **F5A0–F5B2**, coherentes con la tabla de fuente ampliada. **El renderizado en PPSSPP todavía no está validado.**
- **Ensayo de inyección aislada:** [`tools/reinsercion_segura_demo.py`](tools/reinsercion_segura_demo.py). No crea ISO distribuible, ni parchea todos los diálogos.
- **Resultados comprobados:** [`reports/auditoria_binaria_es.json`](reports/auditoria_binaria_es.json). 349 offsets PSPFS intactos y 347 recursos no intervenidos idénticos.
- **Estado lingüístico/QA:** [`reports/qa_traduccion_es.json`](reports/qa_traduccion_es.json). Todavía falta revisión humana y prueba de PPSSPP.

**Prohibido usar el borrador directamente como parche:** falta validar el prototipo de fuente en PPSSPP y la verificación del cargador de compresión, la reconstrucción de longitudes/punteros y la prueba visual en juego. Los archivos binarios originales continúan intactos.

## Prototipo de fuente española — 19 caracteres (validación binaria aprobada)

Se corrigió la incompatibilidad entre el códec inicial `F040–F052` y la tabla real de `FONT.BIN`. La versión experimental utiliza **`F5A0–F5B2`**, sin insertar códigos en medio de los 2.721 registros originales.

- [Patcher experimental de fuente](tools/font_es_patch.py) y [verificador independiente](tools/font_es_guard.py): solo para ISO propia, **nunca subir la ISO candidata ni los atlas originales**.
- [Informe detallado](docs/FUENTE_ES_PROTOTIPO.md): 19 glifos añadidos, 2.721 glifos originales intactos, 348 recursos no relacionados idénticos y 32 bytes de margen.
- [Informe JSON](reports/fuente_es_19_glifos.json) y [cuatro pruebas negativas](reports/fuente_es_pruebas_negativas.json): el verificador rechaza modificaciones de un solo bit en un recurso ajeno, el índice, entradas antiguas de fuente y relleno.
- **No se ha probado el renderizado de los nuevos glifos en PPSSPP ni la reinserción del corpus completo.**

## Revisión contextual y blindaje de reinserción — fase adicional

- [196 correcciones contextualizadas y repetidas de una fase anterior](docs/REVISION_CONTEXTUAL_2026-11-18.md), con [registro individual histórico](qa/revision_contextual_2026-11-18.csv). Ese corte fue de 369 entradas; después las fases 3–5 llegaron a **441 revisadas/normalizadas por IA y 8.794 pendientes**. El avance vigente se presenta en la fase 6.
- [Protocolo de reinserción fail-closed](docs/PROTOCOLO_REINSERCION_FAIL_CLOSED.md) y [verificador global para textos](tools/iso_guard_global.py): **no permite mover offsets, modificar otros recursos ni cambiar formatos de compresión**.
- [Ensayo de dos etapas](reports/aislamiento_combinado_es.json): fuente experimental seguida de una edición de un byte de diálogo; ambos verificadores dieron PASS binario.
- **No confundir aislamiento binario con juego funcional.** No se ha validado el renderizado de glifos ni la visualización de diálogos en PPSSPP.

## Corte anterior (fases 3–5): revisión narrativa, glosario y preinserción — 18/11/2026

- **72 ediciones adicionales** respecto del corte histórico de 369: [57 diálogos, interfaz y efectos](qa/revision_dialogos_glosario_fase3_2026-11-18.csv), [8 correcciones de caracteres invisibles, saltos y terminología](qa/revision_caracteres_y_dialogos_fase4_2026-11-18.csv) y [8 ajustes del nombre New-geon](qa/revision_new_geon_fase5_2026-11-18.csv). Son **73 modificaciones** de registros, pero una corresponde a un registro previamente revisado. Por eso el acumulado crece de 369 a **441**, no 442.
- El [glosario de 67 entradas](traduccion/GLOSARIO_CANONICO.csv) es ahora la fuente terminológica CSV; el archivo `GLOSARIO_PROPUESTA.csv` se conserva únicamente como histórico.
- El [preflight de 9.237 unidades](tools/auditar_preinsercion_es.py) clasifica **4.576 cambios de longitud en scripts**, **280 desbordes de campo**, **816 sin capacidad modelada**, **6 rótulos de imagen**, **2 entradas sin traducción** y **3.557 candidatas únicamente a ensayos**. **Cero entradas están aprobadas para inserción definitiva.**
- [Informe y protocolo](docs/INFORME_PREINSERCION_ESTATICA.md); [estadísticas reproducibles](reports/preinsercion_estatica_2026-11-18.json). La [validación CI](.github/workflows/validacion.yml) ejecuta pruebas, cotejo de originales y un reporte de riesgos por fila en sus artefactos.
- La codificación experimental usa `F5A0–F5B2` y no toca por diseño otros archivos del juego. Los informes previos prueban aislamiento binario en cambios pequeños, **no** que el motor renderice el texto completo, que acepte 19 glifos o que el parche masivo sea seguro.

## Cómo trabajar

1. Consulta [`corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt`](corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt) para lectura global o el CSV maestro para asignar trabajo.
2. Al traducir, **modifica solo `espanol`**, nunca el original, identificadores, formato ni desplazamientos. Mantén todas las variables, secuencias de control y repeticiones.
3. Para registros de `revisar_visibilidad.csv`, comprueba antes si realmente se presentan al jugador, si son etiquetas de depuración o si necesitan reconstruir bytes.
4. Ejecuta `python tools/verificar_integridad.py --raiz .` y las pruebas antes de entregar cambios.

**Documentación:** [metodología](docs/METODOLOGIA.md) · [campos y formato TXT](docs/FORMATO_CORPUS.md) · [auditoría de pendientes](docs/AUDITORIA_PENDIENTES.md) · [controles de calidad](docs/CONTROL_CALIDAD.md) · [reproducibilidad](docs/REPRODUCIBILIDAD.md) · [limitaciones](docs/LIMITACIONES_Y_ROADMAP.md) · [contribuir](CONTRIBUTING.md).

## Reproducibilidad técnica

Python 3.10+ sin bibliotecas externas, sobre una copia propia de la edición PSP identificada en [reproducibilidad](docs/REPRODUCIBILIDAD.md):

```bash
python tools/pipeline.py --iso /ruta/a/Cladun.iso --salida .
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte reports/preflight_local.json --filas reports/preflight_local.csv
```

El proceso identifica ISO9660 → `PSPFS_V1` → contenedores anidados, decodifica fuentes CP932 e indexa textos y metadatos. Los datos intermedios binarios **no se añaden a GitHub**. El TXT es para lectura; el CSV conserva el origen necesario para una eventual reinserción.

## Límites del proyecto

No se incluye una ISO ni archivos gráficos/binarios originales del videojuego. La traducción, la cobertura en pantallas y una versión jugable en PPSSPP están **pendientes**. Si se distribuye una modificación, deberá hacerse mediante un parche que no incluya los recursos comerciales del juego. *Cladun* y sus materiales pertenecen a sus titulares respectivos.

## Blindaje adicional por manifiesto de origen — noviembre de 2026

- [Plan textual verificable](tools/plan_textual_seguro.py): un ID se vincula con sus bytes CP932 originales, reemplazo español codificado, longitud exacta, offset y huella SHA-256 de la ISO privada.
- [Guarda de aislamiento](tools/iso_guard_global.py): exige `--manifest` vinculado al corpus, en lugar de aceptar permisos arbitrarios de bytes; comprueba también los bytes **dentro** de cada tramo autorizado. [Protocolo detallado](docs/MANIFIESTO_TEXTO_EXACTO.md).
- El plan no escribe una ISO ni permite editar retratos, tiles o fuentes. **La inserción masiva y la prueba visual en PPSSPP siguen pendientes.**

## Fase 6: naturalidad y glosario — 18/11/2026

- [33 ajustes narrativos](qa/revision_naturalidad_fase6_2026-11-18.csv) en diálogos de NPC y tutoriales, incluidos fragmentos de una misma frase. CSV, TXT y bilingüe actualizados a la vez.
- **Acumulado: 474 entradas revisadas/normalizadas por IA y 8.761 pendientes** de revisión individual (9.235 borradores). Revisión humana y visual pendientes.
- Glosario canónico ampliado de 63 a **67 términos**; los nombres de habilidades son provisionales hasta probarlos en el juego.
- [Informe reproducible de esta fase](reports/revision_naturalidad_fase6.json). El informe estático previo corresponde al corte anterior; CI realiza un nuevo preflight. **Cero traducciones aprobadas para inserción final.**

## Integración del parche sin modificar assets — fase experimental

- [Integrador append-only](tools/integrar_parche_seguro.py), [recompresor IMY](tools/imy_repack_safe.py) y [protocolo detallado](docs/INTEGRACION_APPEND_ONLY.md). En lugar de ocupar espacio de retratos/tiles, incorpora nuevas versiones de los contenedores **solo textuales** al final de DATA.DAT, preservando bytes y offsets de los recursos no intervenidos.
- [Diagnóstico automatizado](tools/reportar_integrabilidad_es.py): **8.491 sustituciones planificables**, **746 textos que ya coinciden en bytes** y **0 unidades bloqueadas** (280 adaptaciones compactas, 2 fuentes truncadas bajo control por bytes y 6 rótulos gráficos acotados). El conteo se regenera en GitHub Actions; no significa que los 8.203 se hayan insertado realmente.
- [Ensayo estructural local de una única cadena artificial](reports/ensayo_estructura_append_only_2026-11-18.json): 1.625 bloques, 51.705 comandos, 46.308 instrucciones no textuales intactas, 348 recursos PSPFS ajenos idénticos. No hay verificación PPSSPP.
- El modo **estricto** ya reconoce las 9.237 unidades y prepara una **candidata privada**, pero sigue sin ser parche final aprobado. La publicación es atómica y la ISO original se comprueba de nuevo.
- No se publican ISO ni recursos comerciales. El **parche español completo todavía no está aprobado**: falta demostrar carga de la nueva ubicación PSPFS, render de la fuente y funcionamiento de la candidata completa en PPSSPP.

- [Informe de seis rótulos en una ISO privada real](reports/ensayo_graficos_iso_2026-11-18.json): 348 recursos PSPFS ajenos y 11 archivos ISO9660 idénticos en offsets y bytes; solo los píxeles de texto autorizados se modifican.
- [Adaptaciones de campos fijos](tools/ajustes_campos_es.py) y [localizador gráfico](tools/graficos_texto_es.py). Los borradores completos no se reemplazan: las abreviaturas pertenecen exclusivamente al empaquetado.
- **100 % significa cobertura estructural de inserción, no 100 % de diálogos verificados narrativamente ni 100 % de funcionamiento comprobado.**

- [Prueba de códec sobre la ISO original (19/11/2026)](reports/roundtrip_imy_multibloque_iso_real_2026-11-19.json): reempaquetado de 8 bloques IMY de SCRIPT.SDT y 5 de DATABASE.DAT, recuperando todos los bytes originales en la decodificación posterior. Se corrigió la cabecera para conservar el tamaño real por bloque (`131072` bytes), no el tamaño total del recurso. **No implica PPSSPP verificado.**

- [Exportador de parche BPS diferencial](tools/generar_parche_bps.py) y [protocolo de uso](docs/PARCHE_BPS_EXPERIMENTAL.md): a partir de una ISO candidata privada creada por el integrador, produce un archivo BPS experimental solo tras reconstruir exactamente la candidata desde la ISO original y comprobar que los assets no textuales sean idénticos. Requiere `--experimental`; no acredita aún PPSSPP ni constituye un lanzamiento final.

## Parcheador gráfico para Windows (descarga sin instalar Python)

- **[Parcheador Windows x64 — GitHub Releases](https://github.com/ARivas3008/loxalizacion-cladun-psp/releases/tag/parcheador-v0.1.0)**. El workflow [Compilar parcheador Windows](.github/workflows/parcheador-windows.yml) genera el ejecutable sin dependencias externas para usuarios finales y lo publica como versión preliminar.
- **[Código fuente, pruebas, guía y controles de integridad](patcher/README.md)**. Admite BPS1, verifica SHA-256 de ISO original y CRC32, muestra progreso y nunca sobrescribe la imagen original.
- **Nota:** actualmente hay un **aplicador** de BPS, pero **todavía no existe una versión final del parche español comprobada en PPSSPP**. No confundir el ejecutable con un parche jugable ni dar por demostrada la integridad de los assets de un BPS arbitrario.
