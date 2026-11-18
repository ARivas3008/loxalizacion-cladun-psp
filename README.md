# CLADUN: This Is an RPG! — Corpus para localización al español (PSP USA)

Repositorio de **texto original sin traducir**, extraído y auditado de una copia identificada de *Cladun: This Is an RPG!* para PSP. La unidad de trabajo es **cada cadena traducible o potencialmente visible** (diálogos, opciones, menús, nombres, descripciones, mensajes, créditos y rótulos gráficos), no las instrucciones del motor.

> **Estado: extracción revisada, cobertura no certificada.** Se revisaron estructuralmente los campos de las tablas conocidas, pero todavía faltan pruebas de pantalla en PPSSPP y algunos recursos gráficos/ejecutables. No se declara que esté recuperado el 100 % de los textos visibles.

## Descargar y trabajar

| Archivo | Propósito |
| --- | --- |
| [`corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt`](corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt) | **Lectura principal:** todos los bloques numerados, identificados y **sin traducir** |
| [`corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv`](corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv) | **Fuente maestra editable:** mismos bloques, offsets, estado y columna `espanol` vacía |
| [`corpus/confirmados_formato.csv`](corpus/confirmados_formato.csv) | Subconjunto reconocido como cadena/campo por su estructura, **no validado visualmente en todos los casos** |
| [`corpus/revisar_visibilidad.csv`](corpus/revisar_visibilidad.csv) | Cadenas reales cuyo uso en pantalla debe confirmarse y dos campos con bytes incompletos |
| [`qa/decisiones_auditoria.csv`](qa/decisiones_auditoria.csv) | Trazabilidad de exclusiones, correcciones y recuperaciones respecto de la extracción anterior |
| [`reports/resumen.json`](reports/resumen.json) | Recuentos verificables y huella digital de la ISO estudiada |

### Recuento — auditoría de 17 de noviembre de 2026

- **9.237 bloques** en el corpus maestro, una cadena por bloque.
- **8.202** registros en estructuras/campos reconocidos, incluido el texto gráfico examinado visualmente.
- **1.033** cadenas textuales cuyo uso en pantalla requiere comprobación.
- **2** campos japoneses con bytes CP932 truncados que deben cotejarse antes de traducir.
- **127** cadenas genuinas recuperadas que el filtro anterior había omitido.
- **133** correcciones de texto/posición (incluidos nombres de mazmorras con un carácter prefijado erróneamente y espacios originales que se habían perdido).
- **56** falsos positivos numéricos, **32** falsas detecciones fuera de campos y **64** nombres internos de archivo apartados del corpus.

Los recuentos representan **instancias de origen**, no frases distintas. Las repeticiones y los identificadores originales se conservan para la futura reinserción. El orden es el del **recurso/bloque/campo**, no necesariamente el cronológico de la historia.

## Normas de trabajo

1. **Nunca** cambies `grupo_id`, `text_id`, `original`, `origen`, offsets o el orden de registros.
2. Escribe la futura traducción exclusivamente en `espanol`; el TXT se regenera desde el CSV maestro.
3. Conserva las variables de formato, los códigos de control, los saltos de línea y las referencias contextuales. No inventes texto donde haya bytes dañados.
4. En `requiere_comprobar_en_juego`, confirma si la cadena aparece en pantalla antes de darla por lista para localización.
5. Un PNG con rótulos requiere edición gráfica: modificar el CSV/TXT no sustituye los píxeles de la imagen.

## Reproducibilidad

Requiere Python 3.10+ y una copia propia de la **ISO del mismo juego y región**. No requiere paquetes de terceros.

```bash
python tools/extract_cladun.py /ruta/Cladun_USA.iso -o build
python tools/revisar_corpus.py --iso /ruta/Cladun_USA.iso --raw build/corpus/todo_el_texto.csv --salida .
python tools/validar_corpus.py
python -m unittest discover -s tests -v
```

La primera orden crea inventarios **temporales de extracción** en `build/` (ignorados por Git); **no publica instrucciones ni opcodes** como corpus. La segunda lee las posiciones reales de los campos, elimina falsos positivos, corrige fuentes y regenera el CSV/TXT maestro.

Huella SHA-256 de la ISO examinada: `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f` (volumen `CLASSIC_DUNGEON_TRIAL_AND_APPEND`; identificador de título `NPUH10072`). Una edición o revisión distinta puede requerir un análisis nuevo.

## Documentación

- [Alcance, estructura y criterios de clasificación](docs/01_ALCANCE_Y_CRITERIOS.md)
- [Formato de CSV y texto plano](docs/02_FORMATO_Y_TRAZABILIDAD.md)
- [Auditoría de los textos pendientes](docs/03_AUDITORIA_Y_HALLAZGOS.md)
- [Pruebas de calidad y preparación para traducción](docs/04_CONTROL_DE_CALIDAD.md)
- [Limitaciones y siguientes verificaciones](docs/05_LIMITACIONES.md)
- [Historial de decisiones](CHANGELOG.md)

## Derechos

Este es un proyecto de investigación técnica de localización. Los textos, nombres, imágenes y demás recursos del videojuego pertenecen a sus titulares. **La licencia de este repositorio, cuando corresponda, se aplica únicamente al código original del proyecto, no a los materiales extraídos del juego.** No se distribuyen ISOs ni los binarios, gráficos, fuentes o audio comerciales. Para distribuir una traducción funcional, lo apropiado es crear un parche que requiera los archivos legítimos del juego.
