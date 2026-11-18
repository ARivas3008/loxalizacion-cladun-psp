# CLADUN: This Is an RPG! — Localización al español (PSP)

> **Estado:** corpus original intacto y auditado; borrador de traducción automatizada al español (9.235 de 9.237 posiciones), **no validado narrativamente ni apto para reinserción**. Cobertura absoluta sin demostrar.

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

Se conservaron los 9.237 IDs y originales, y se generó un **borrador separado**, sin sobrescribir el corpus fuente. Incluye 9.235 entradas con texto español; dos campos con bytes CP932 incompletos siguen pendientes. Solo 67 entradas recibieron post-edición contextual por IA; el resto **no** tiene validación narrativa individual.

| Material | Archivo |
| --- | --- |
| Guion original estilo FAQ (extracción anterior) | [`corpus/LECTURA_ORIGINAL_ESTILO_FAQ.txt`](corpus/LECTURA_ORIGINAL_ESTILO_FAQ.txt) |
| Texto español continuo, borrador | [`traduccion/CLADUN_BORRADOR_ES.txt`](traduccion/CLADUN_BORRADOR_ES.txt) |
| Lectura bilingüe y cotejo | [`traduccion/CLADUN_BORRADOR_BILINGUE_FAQ.txt`](traduccion/CLADUN_BORRADOR_BILINGUE_FAQ.txt) |
| CSV bilingüe con metadatos originales | [`traduccion/CLADUN_BORRADOR_ES.csv`](traduccion/CLADUN_BORRADOR_ES.csv) |
| Incidencias de QA | [`traduccion/INCIDENCIAS_QA.csv`](traduccion/INCIDENCIAS_QA.csv) |
| Glosario provisional | [`traduccion/GLOSARIO_PROPUESTA.csv`](traduccion/GLOSARIO_PROPUESTA.csv) |
| Informe técnico y lingüístico | [`docs/INFORME_TRADUCCION_2026-11-18.md`](docs/INFORME_TRADUCCION_2026-11-18.md) |

**Aviso:** los signos españoles no se pueden representar directamente con CP932; falta adaptar codificación/fuentes, revisar texto y probar el juego en PPSSPP. Ninguna traducción está aprobada para insertar todavía.

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
```

El proceso identifica ISO9660 → `PSPFS_V1` → contenedores anidados, decodifica fuentes CP932 e indexa textos y metadatos. Los datos intermedios binarios **no se añaden a GitHub**. El TXT es para lectura; el CSV conserva el origen necesario para una eventual reinserción.

## Límites del proyecto

No se incluye una ISO ni archivos gráficos/binarios originales del videojuego. La traducción, la cobertura en pantallas y una versión jugable en PPSSPP están **pendientes**. Si se distribuye una modificación, deberá hacerse mediante un parche que no incluya los recursos comerciales del juego. *Cladun* y sus materiales pertenecen a sus titulares respectivos.
