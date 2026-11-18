# Cladun: This Is an RPG! (PSP USA) — Extracción para traducción al español

Proyecto de localización centrado **exclusivamente en los textos visibles y localizables** de la versión de PSP suministrada: diálogos, respuestas, nombres, descripciones, pantallas, HUD, tutoriales, créditos y rótulos de imágenes.

**No se incluyen listados de instrucciones/opcodes del juego.** El extractor las lee internamente cuando son necesarias para identificar las cadenas, pero entrega archivos con **texto original y columna para traducción**, manteniendo ID, origen y orden.

## Archivos que debes usar

| Archivo | Contenido |
| --- | --- |
| [corpus/textos_para_traducir.csv](corpus/textos_para_traducir.csv) | **Índice maestro** de todos los textos identificados o candidatos por validar, en orden de extracción |
| [corpus/confirmados.csv](corpus/confirmados.csv) | Textos no vacíos extraídos de estructuras conocidas, más rótulos gráficos comprobados |
| [corpus/pendientes_validacion.csv](corpus/pendientes_validacion.csv) | Cadenas detectadas en bases de datos sin campos completamente documentados; **pueden contener falsos positivos** |
| [corpus/textos_graficos.csv](corpus/textos_graficos.csv) | Rótulos encontrados visualmente en las seis imágenes PNG de `SYS.DAT2` inspeccionadas; la edición requerirá modificar imágenes |
| [corpus/dialogos.csv](corpus/dialogos.csv) | Diálogos, nombres de interlocutor y opciones (fuente sin filtrar; incluye vacíos) |
| [corpus/interfaz_hud.csv](corpus/interfaz_hud.csv) | Mensajes de interfaz y sistema, con marcadores de formato |
| [corpus/objetos_lugares_personajes.csv](corpus/objetos_lugares_personajes.csv) | Nombres/descripciones de equipo, personajes, magia, enemigos y lugares; **revisión pendiente de estructura** |
| [corpus/creditos.csv](corpus/creditos.csv) | Créditos en orden de origen, incluidos los espacios de formato |

**Resumen de esta edición:** 9.647 registros brutos; 6.397 textos confirmados no vacíos; 2.803 candidatos textuales por validar; 10 referencias a textos de imágenes comprobados visualmente y 2 rótulos gráficos por validar. Se han apartado 391 registros vacíos y 56 falsos positivos numéricos de `LV.DAT`. **Total del índice maestro: 9.212 entradas**, incluidas las pendientes. Los números son **entradas de origen, no frases únicas**.

> **Cobertura:** estos resultados NO demuestran todavía el 100 % del texto del juego. Faltan auditar completamente rótulos gráficos de otros recursos, campos binarios, cadenas del ejecutable y comprobación práctica en PPSSPP. [Informe de cobertura](reports/AUDITORIA_COBERTURA_2026-11-17.md).

## Cómo traducir

1. Abre `corpus/textos_para_traducir.csv` (UTF-8 con BOM). Cada fila tiene `text_id`, `texto_original`, `traduccion_es`, `tipo`, `fuente` y localización original.
2. Escribe el español **únicamente en `traduccion_es`**. Nunca edites el `text_id`, el texto fuente ni el orden. Es válido conservar repeticiones: pueden usarse en contextos diferentes.
3. Da prioridad a filas `validacion_fuente=confirmado_estructura` o `confirmado_visual`. Las `pendiente_validacion` deben investigarse antes de integrarlas.
4. Conserva las variables, por ejemplo `%s`, `%d`, `%02d`, las secuencias de control y los saltos de línea. La columna `longitud_original_bytes` **no representa por sí sola el límite máximo** que acepta el motor.
5. En los rótulos de `SYS.DAT2/*.PNG`, cambiar el CSV **no cambia la imagen del juego**: se necesita una edición gráfica y reinserción específica.

## Organización

```text
corpus/
  textos_para_traducir.csv    <- índice principal y único para reparto de traducción
  confirmados.csv             <- texto de fuentes reconocidas
  pendientes_validacion.csv   <- candidatos, no publicar traducciones sin validar
  textos_graficos.csv         <- palabras rasterizadas en PNG comprobados
  dialogos.csv                <- subconjunto original de diálogos
  interfaz_hud.csv            <- interfaz
  objetos_lugares_personajes.csv
  creditos.csv
  todo_el_texto.csv           <- extracción bruta para auditoría, NO lista de traducción
reports/
  resumen_localizacion.json   <- recuentos del corpus de trabajo
  registros_no_traducibles.csv <- filas vacías y falsos positivos apartados
  AUDITORIA_COBERTURA_2026-11-17.md
indices/                      <- solo índices de procedencia y bloque, NO instrucciones
  iso9660.csv
  pspfs.csv
  dsarc.csv
  script_blocks.csv
  database_records.csv
tools/
  extract_cladun.py           <- localiza el texto desde la ISO suministrada
  build_translation_corpus.py <- genera los CSV para traductores
tests/
```

## Reproducir sin publicar el contenido binario del juego

Utiliza una copia propia de la ISO USA suministrada y Python 3.10+:

```bash
python tools/extract_cladun.py ruta/al/juego.iso -o .
python tools/build_translation_corpus.py --root .
python -m unittest discover -s tests -v
```

La ISO auditada tiene volumen `CLASSIC_DUNGEON_TRIAL_AND_APPEND`, ID PSP `NPUH10072` y SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.

**Avisos:** No se ha implementado todavía un inyector de texto ni comprobado la traducción en consola. No subas la ISO, audio, gráficos ni otros recursos originales comerciales al repositorio público. *Cladun* y sus materiales pertenecen a sus titulares de derechos.
