# Reglas para el proyecto de localización española de Cladun PSP

Este proyecto se dedica a **texto que ve el jugador**, no a documentar instrucciones del motor del juego.

1. Empezar por `corpus/textos_para_traducir.csv`; **no utilizar** `corpus/todo_el_texto.csv` como lista de trabajo (es la extracción bruta).
2. Conservar `text_id`, `texto_original`, `fuente`, `indice_bloque`, `orden_en_bloque`, `offset_hex` y el orden de las filas. No unir/desduplicar líneas aunque el texto coincida.
3. Escribir la traducción solo en `traduccion_es`; guardar notas contextuales aparte. No convertir nombres, variables o bytes en frases inventadas.
4. No traducir automáticamente `pendiente_validacion`: primero identificar el campo real en el juego. Los 56 falsos positivos de `LV.DAT` ya están apartados.
5. Proteger marcadores de formato (`%s`, `%02d`, `%d`, etc.) y saltos de línea; comprobar espacio de cuadros y tamaño en bytes **antes de reinsertar**.
6. El texto de archivos PNG es texto **gráfico**: traducirlo implica modificar la imagen, no un CSV binario.
7. Mantener separados corpus para traductores, reporte de auditoría e índices internos. No reintroducir listados de opcodes o instrucciones en el repositorio de traducción salvo petición expresa.
8. No afirmar extracción completa al 100 % sin verificar todas las fuentes gráficas, campos no documentados, ejecutable y juego en PPSSPP.
9. No subir ISOs, juegos, audio, sprites, PNG originales, descompresiones completas ni firmware.
10. Validar antes de publicar con `python -m unittest discover -s tests -v` y mantener trazabilidad de los cambios.
