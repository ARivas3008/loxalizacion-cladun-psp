# CLADUN — Localización española (PSP, USA)

Proyecto de **extracción, indexación y futura localización** de los textos de *Cladun: This Is an RPG* para PSP (región USA). El propósito es conservar el orden lógico de los scripts, la ubicación exacta de cada cadena y los datos necesarios para revisar la traducción sin modificar la ISO original.

> **Estado actual:** extracción de texto en fase de auditoría. Se han identificado y descomprimido todas las entradas del contenedor `PSPFS_V1` de la imagen analizada, pero **no está certificado que se haya recuperado absolutamente todo el texto visible en el juego**: hay gráficos, formatos binarios de campos no documentados y texto eventualmente incrustado en código/recursos que requieren verificación visual.

## Resultados de la versión analizada

- Imagen fuente: `CLASSIC_DUNGEON_TRIAL_AND_APPEND`, 305.496.064 bytes (ISO9660).
- Contenedor principal: `PSP_GAME/USRDIR/DATA.DAT`, 349 de 349 archivos procesados.
- 1.186 archivos internos en paquetes `DSARC FL` y `DSARCIDX`.
- `SCRIPT.SDT`: `SCRIPT.DAT` y `AISCRIPT.DAT`, con 1.625 y 552 bloques respectivamente.
- 73.240 instrucciones indexadas, y 5.397 instrucciones de texto del guion (incluidas 190 cadenas vacías).
- `DATABASE.DAT/STRTBL.DAT`: 651 cadenas del sistema y 3 posiciones vacías en la tabla de punteros.
- Total: 9.647 registros de texto, **incluidos candidatos no confirmados** y líneas vacías de créditos.
- Los resultados exactos y las reservas están en [`reports/cobertura.json`](reports/cobertura.json).

## Estructura

```text
.
├── README.md
├── AGENTS.md
├── .gitignore
├── tools/
│   └── extract_cladun.py
├── tests/
│   └── test_extract_cladun.py
├── indices/
│   ├── iso9660.csv           # orden de la ISO y offsets
│   ├── pspfs.csv             # 349 archivos en su orden original
│   ├── dsarc.csv             # tablas de archivos internos
│   ├── script_blocks.csv     # identificadores, .dsf y rango de bytes
│   ├── script_commands.csv   # 73.240 instrucciones; en el ZIP completo
│   ├── comandos/             # índice dividido para consulta en GitHub
│   │   ├── parte_01.csv      # comandos 1–5.000
│   │   ├── ...
│   │   └── parte_15.csv      # comandos 70.001–73.240
│   └── database_records.csv  # estructura por registro, cuando es deducible
├── corpus/
│   ├── todo_el_texto.csv     # catálogo principal para localización
│   ├── dialogos.csv
│   ├── interfaz_hud.csv
│   ├── objetos_lugares_personajes.csv
│   └── creditos.csv
├── reports/
│   ├── cobertura.json
│   └── textos_binarios_no_confirmados.csv
└── docs/
    ├── EXTRACCION.md
    ├── FORMATOS.md
    └── CONTROL_CALIDAD.md
```

**Nota sobre GitHub:** el índice de 73.240 comandos está publicado íntegro y ordenado en los 15 archivos de `indices/comandos/`, debido al tamaño del CSV unificado. El extractor genera asimismo `indices/script_commands.csv`, incluido en el paquete ZIP descargable del proyecto. No hay pérdida de filas ni de orden.

## Cómo reproducir la extracción

1. Extrae la ISO de tu archivo `.7z` con 7-Zip. **No subas la ISO ni los archivos binarios originales a un repositorio público.**
2. Instala Python 3.10 o posterior (no se necesitan librerías externas).
3. Desde la raíz del proyecto ejecuta:

```bash
python tools/extract_cladun.py "C:/ruta/Cladun_This_Is_An_RPG_USA_PSN_PSP-PLAYASiA.iso" -o .
python -m unittest discover -s tests -v
```

Los CSV son UTF-8 con BOM (compatibles con Excel en español), usan encabezados en inglés para mantener un esquema estable y ofrecen una columna `translation_es` en blanco. Cada `text_id` referencia la **versión y orden de extracción** y se acompaña de offsets, nombres de script, opcode, índice y bytes de origen. Conservar `text_id`, `source`, `script_id`, `offset_hex` y `raw_hex` al traducir.

## Interpretación correcta de los datos

- **Confirmado**: extracción conforme a una estructura conocida (`SCRIPT.DAT`, `STRTBL.DAT`, tabla de nombres de tamaño fijo o créditos).
- **Candidato**: aparente texto encontrado mediante detección de cadenas en los registros binarios. Puede contener fragmentos o prefijos de bytes que no son parte del texto; **requiere revisión manual**.
- `reports/textos_binarios_no_confirmados.csv` conserva pistas adicionales y puede incluir falsos positivos (metadatos de imágenes, nombres de archivos o basura binaria). **No traducir ni integrar automáticamente**.
- No hay aún editor/reinserción, prueba en PPSSPP ni OCR de textos dibujados como píxeles.

## Flujo de localización

1. Auditar fuentes y candidatos en sus índices.
2. Validar las etiquetas `category`/`confidence`, asociar interlocutores y las líneas que forman un mismo diálogo.
3. Traducir **solo `translation_es`**, manteniendo variables, espacios críticos y códigos en los textos.
4. Verificar encoding, anchura de cuadros, consistencia de términos, límites de bytes y estructura de cada registro.
5. Implementar la reinserción con pruebas binarias y probar en PPSSPP antes de distribuir un parche que no incluya contenido del juego.

## Proveniencia y atribuciones técnicas

Se inspeccionaron directamente los archivos de la ISO facilitada para la auditoría. La implementación IMY sigue la descripción del formato y el comportamiento publicado en [ProgSys/pg_disatools](https://github.com/ProgSys/pg_disatools) (licencia MIT en su código), y se comprobó localmente contra los tamaños expandidos de los 349 archivos. Este repositorio contiene datos de trabajo derivados de la copia analizada; *Cladun* y todos sus materiales pertenecen a sus titulares de derechos. Este proyecto no está afiliado a Nippon Ichi Software ni a NIS America.
