# Beta provisional — R52 completo / R43 control / R56 alternativa

Base: fad0c43dde4db3d6bf36b1016aed24d00c60ce3f. PR #7 permanece DRAFT sin modificaciones. CI de la base: 45715998977 y 45715985688 SUCCESS. No se certifica ejecución de la nueva beta.

## Preflight real (25/11/2026)

ISO USA aportada, extraída localmente mediante libarchive: 305496064 B, SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. Analizador independiente: 16 entradas ISO9660 (12 archivos), 349 PSPFS dentro de límites, SCRIPT.SDT descomprimido, cuatro hijos DSARC, 1625 scripts, 51705 comandos, 5397 textuales, 46308 no textuales. SCRIPT.DAT SHA c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358. SCRIPT.TBL SHA f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37. Esto verifica SOLO la ISO original.

## Construcción privada (no ejecutada en el entorno actual)

Desde el checkout de esta rama, Python 3.12, instalar dependencias del repositorio. Las rutas de salida han de ser nuevas, externas al checkout.

```sh
python -m tools.beta_provisional --iso /PRIVADO/USA.iso --output /PRIVADO/beta-r43 --profile r43
python -m tools.beta_provisional --iso /PRIVADO/USA.iso --output /PRIVADO/beta-r52 --profile r52 --acepto-beta-experimental
python -m tools.beta_provisional --iso /PRIVADO/USA.iso --output /PRIVADO/beta-r56 --profile r56 --acepto-beta-experimental
```

R43 8214+1/8248, 0 desplazados. R52 8247+1/8248 planificados, 146 desplazados (104 no textuales, 24 bloques). R56 8236+1/8248, 28 desplazados (5 no textuales). No reducir los textos originales en el corpus, ni añadir cajas sin presupuesto. No exportar BPS, publicar activos o fusionar.

## Betatesting

Primero gate estática con reapertura de candidata, tablas y hermanos exactos, 46308 comandos no textuales exactos, número de sustituciones y desplazamientos esperado. Luego PPSSPP oficial 1.20.4, comparar USA/R43/R52 con partidas nuevas independientes: arranque, opciones, prólogo completo y skip, pueblo, diálogo, combate, segundo nivel, enciclopedia, guardado y carga. R52: ejecutar los 146 casos individuales producidos en movement_qa.csv y registrar PC/estado/retorno y evidencia auténtica por comando; 104 no textuales prioritarios. No confundir un comando localizado estáticamente con uno ejecutado. Si falla R52, repetir escena en R56 y R43 y aislar bloque; volver a R43 para pruebas generales. Q001–Q042 y casos adicionales del CSV de QA mantienen sus estados previos hasta nueva evidencia específica de la candidata. Las ligaduras, fuente y gráficos requieren QA visual.

Estado: preflight A ejecutado; constructor y tests añadidos; ninguna candidata acumulada reconstruida aquí, ninguna sesión PPSSPP nueva, 0/146 dinámicos. El entorno no tiene PPSSPP ni DNS directo a GitHub. No se modifica el perfil oficial.
