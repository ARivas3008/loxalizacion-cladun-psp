# Revisión selectiva de rarezas · Cladun PSP

Se revisaron las alertas emitidas por el guion bilingüe reconstruido, contrastando las intervenciones completas con el inglés. Se propone un conjunto **conservador de 687 cambios de la columna `espanol`**, manteniendo 8.550 filas del corpus sin modificar. La corrección se aplica en la rama `revision-manual-dialogos`, nunca en `main` ni directamente a la ISO.

## Qué se corrige y qué no

- Corrige puntos introducidos por traducir porciones de una misma oración de forma aislada, sujetos y tiempos verbales incoherentes, frases partidas con contenido duplicado y nombres propios convertidos en verbos o sustantivos comunes por traducción automática.
- Una coincidencia del detector **no es una orden de corrección**: las pausas expresivas aceptables se conservan y las traducciones plausibles de sobrenombres se dejan pendientes de contexto visual.
- No altera los bytes originales, orden de filas, IDs, offsets, marcadores del motor, fuentes, gráficos, ni el paquete de la ISO.
- Dos fragmentos japoneses defectuosos permanecen sin traducción; no se reconstruyen por adivinación.

## Archivos de control

- `qa/revision_rareza_2026-11-20.csv`: libro mayor auditable con `text_id`, valor anterior, valor corregido, justificación y segmento. **Única fuente de estos cambios.**
- `qa/alertas_reconstruccion_antes_revision.csv`: copia de las alertas de partida, para impedir que el importador modifique entradas fuera de lo detectado.
- `tools/aplicar_revision_rareza.py`: validador e importador de preimagen exacta (modo seco por defecto, escritura solo con `--aplicar`). Ejecuta el importador ya existente y reconstruye las vistas.
- `qa/INFORME_REVISION_RAREZA_2026-11-20.json`: recuentos generados al aplicar.
- `qa/REVISION_RAREZA_PENDIENTES.csv`: lista residual de dudas para revisión humana con captura/escena.

## Comandos de verificación

```sh
python tools/aplicar_revision_rareza.py
python -m unittest discover -s tests -p test_revision_rareza.py -v
python tools/aplicar_revision_rareza.py --aplicar
python tools/verificar_borrador_es.py
python tools/reconstruir_guion_completo.py
```

Para editar a mano el resultado, sigue utilizando `editor/Cladun_Editor_Offline.html`. La importación está condicionada a los campos originales inmutables. Una aprobación editorial **no prueba que la fuente PSP renderice tildes y líneas correctamente** ni genera de por sí un nuevo `.exe` con el parche incorporado.
