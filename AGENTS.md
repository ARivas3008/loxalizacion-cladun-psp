# Reglas del proyecto para revisores y agentes

1. Leer `README.md`, `docs/FORMATOS.md`, `docs/CONTROL_CALIDAD.md` y `reports/cobertura.json` antes de modificar un corpus.
2. **No reordenar, renumerar, eliminar, concatenar ni desduplicar** entradas del corpus. Las repeticiones son intencionales y el orden es un dato de origen.
3. Usar `text_id` + `source` + `offset_hex` + `raw_hex` como identificadores de control de integridad; nunca inferir identidades de personajes o lugares sin contexto.
4. No alterar `original`, `raw_hex`, `script_id`, `file_index`, `command_index`, `opcode_hex`, `instruction_id` ni los índices. Escribir exclusivamente en `translation_es` y `review_status` al localizar.
5. Preservar literalmente formato y marcadores: `%s`, `%d`, `%02d`, `%3d`, secuencias de control, saltos, comillas y símbolos de variables. No traducir el contenido de los marcadores.
6. Las entradas `confidence=candidato` requieren investigación binaria antes de declararlas confirmadas; pueden tener texto accidental generado por el escáner.
7. No afirmar cobertura total del juego hasta auditar gráficos, ejecutable, llamadas de UI y validar en PPSSPP, con pruebas en juego.
8. No versionar ISOs, roms, archivos `.DAT` completos originales, gráficos, audio, ejecutables cifrados, fuentes o descompresiones completas.
9. Antes de un cambio estructural ejecutar `python -m unittest discover -s tests -v` y registrar la versión de la imagen de origen en los reportes.
10. Para futuras traducciones, trabajar en ramas o PR independientes y registrar entradas afectadas, decisiones terminológicas y estado de QA.
