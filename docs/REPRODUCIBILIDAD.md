# Reproducibilidad y procedencia

## Identificación de la versión analizada

- Juego: *Cladun: This Is an RPG!* (USA/PSP).
- ID PSP comprobado: `NPUH10072`.
- Nombre de volumen: `CLASSIC_DUNGEON_TRIAL_AND_APPEND` (identificador técnico; **no** implica por sí solo que la copia tenga únicamente una demo).
- SHA-256 de la ISO usada: `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- SHA-256 del archivo `PSP_GAME/USRDIR/DATA.DAT`: `7f4db811e5d079ed58c15ee21cc14ab472d58d93f5c97378982a922c39af3404`.
- 349 entradas descomprimidas de PSPFS y 1.186 archivos internos de contenedores DSARC catalogados en el proceso de inspección.

## Regeneración del corpus final

Utiliza una copia propia de **esta misma edición** y Python 3.10+:

```bash
python tools/pipeline.py --iso "/ruta/Cladun.iso" --salida .
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz . --guardar
```

El orquestador trabaja con archivos intermedios en un directorio temporal, llama a `extract_cladun.py`, luego a `revisar_corpus.py` y ejecuta QA. **No exporta comandos del motor** ni recursos comerciales dentro del resultado final.

Los programas `tools/extract_cladun.py` y `tools/revisar_corpus.py` documentan los campos por formato y sus offsets. Los TXT y CSV deben mantenerse sincronizados a partir de la misma ejecución. Si una nueva edición de la ISO tiene otro hash o estructuras diferentes, detener el pipeline y auditar antes de fusionar resultados.

## Qué puede y qué no puede reproducirse

- Sí: cadenas recuperadas con los parsers actuales, orden por fuente, bytes y offsets, estados y recuentos.
- No todavía: cobertura total de texto renderizado, pruebas funcionales en PPSSPP, traducción final, tipografías, parche de reinserción y distribución jugable.

Por derechos de autor no se añaden ni redistribuyen ISO, ejecutables, datos, archivos de imagen o sonido originales. El repositorio solo reúne herramientas y corpus destinado a la labor de localización solicitada sobre una copia del juego.
