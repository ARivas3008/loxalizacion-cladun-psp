# Reglas para colaboradores y agentes de localización

**Objetivo exclusivo:** recuperar, auditar, ordenar y traducir las cadenas de texto que pueda presentar *Cladun: This Is an RPG!* (USA, PSP). **No** inventariar como entregable operaciones/opcodes del motor.

1. La **fuente de verdad** es `corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv`. El `.txt` es una exportación de lectura generada desde ese CSV.
2. No insertar texto español hasta que exista una traducción aprobada. Los valores de `espanol` están deliberadamente vacíos.
3. No cambiar ni reordenar `grupo_id`, `text_id`, `original`, offsets, archivos, índices o referencias. No unir cadenas repetidas aunque parezcan iguales.
4. Diferenciar `pendiente_traduccion`, `requiere_comprobar_en_juego` y `requiere_reconstruccion`. **Campo identificado no significa texto visto en pantalla**.
5. No traducir nombres de archivos internos (`rmap*.dat`), números binarios interpretados como texto, controles del motor, nombres comerciales protegidos o marcas gráficas decorativas. Las exclusiones tienen auditoría.
6. En caso de bytes CP932 truncados, conservar el texto con marca `�` y el hexadecimal en `bytes_hex`: nunca reconstruir por conjetura.
7. Toda modificación de la extracción requiere verificación con bytes originales, ubicación reproducible, nota de QA y actualización de `reports/resumen.json`.
8. No publicar la ISO, archivos binarios, imágenes del juego ni recursos comerciales. Evitar divulgar el TXT completo en copias no autorizadas; revisar las implicaciones de derechos para cualquier publicación.
9. La traducción futura se hará solo en `espanol`, respetando `%s`, `%d`, otras variables, glifos especiales y saltos de línea. Probar en PPSSPP antes de aprobar la reinserción.
10. Ejecutar `python tools/validar_corpus.py` y `python -m unittest discover -s tests -v` antes de cambios a `main`.

Consultar `docs/` para definiciones exactas y estado de cobertura. No declarar «100 % extraído» sin recorrido visual y comparación de recursos.
