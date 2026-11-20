# Rama de revisión manual de Cladun: diálogos y hablantes

**Objetivo:** facilitar la corrección humana del español y la lectura por personaje sin manipular binarios de PSP, ISO, recursos artísticos, offsets ni instrucciones del juego.

## Inicio rápido sin instalar nada

1. Abre `editor/Cladun_Editor_Offline.html` con doble clic (Chrome, Edge o Firefox actualizado).
2. Carga `traduccion/CLADUN_BORRADOR_ES.csv` desde el explorador.
3. Busca texto, escena, ID o personaje, cambia solo **Español** y exporta `CLADUN_BORRADOR_ES_CORREGIDO.csv`.
4. Consulta `lectura/CLADUN_GUION_CON_HABLANTES_ES.txt` para el contexto; el original en inglés aparece junto a cada texto.
5. Para aplicar formalmente cambios al repositorio, sigue [la guía](docs/GUIA_EDICION_MANUAL.md) o el [PDF](docs/GUIA_EDICION_MANUAL.pdf).

### Archivos nuevos de esta rama

| Ruta | Uso |
|---|---|
| `editor/Cladun_Editor_Offline.html` | Editor offline en navegador, sin modificar la ISO |
| `lectura/CLADUN_GUION_CON_HABLANTES_ES.txt` | Guion con nombres explícitos 0x6E y marcas de atribución probable |
| `lectura/CLADUN_LECTURA_TOTAL_CON_HABLANTES_ES.txt` | Guion y todos los demás textos, sin perder ninguno de los 9.237 registros |
| `lectura/CLADUN_AUDITORIA_HABLANTES.csv` | Correspondencia ID/escena/nombre y grado de certeza |
| `lectura/CLADUN_RESUMEN_HABLANTES.json` | Conteos y hashes de origen |
| `tools/generar_guion_hablantes.py` | Regeneración reproducible del TXT |
| `tools/aplicar_correcciones_editor.py` | Validación fail-closed y sincronización de TXT/CSV y bitácora de cambios |
| `docs/GUIA_EDICION_MANUAL.md` / `.pdf` | Manual de edición y diagnóstico de tipografía |
| `tests/test_guion_hablantes.py` | Pruebas de atribución conservadora y preservación del origen |

**Nota:** el corpus original tiene 400 campos de nombre de interlocutor, pero no todos los 4.694 diálogos poseen un nombre verificable en el CSV. En escenas sin marcador explícito cercano se imprime `HABLANTE NO VERIFICADO`. Nunca se deben inventar esos hablantes.

**Caso de la captura:** la frase está correctamente escrita en el CSV y mal espaciada en pantalla. No sustituir caracteres españoles por letras sin tilde sin comprobar antes el avance de glifos y el ajuste de línea en PPSSPP. El editor ofrece alertas **orientativas**, no una simulación exacta de ancho gráfico.

No subir binarios del juego, ni una ISO, ni retratos, tiles, atlas o sprites. Esta rama es de corrección de datos textuales; no constituye un parche completamente validado.

## Referencia editorial cruzada: La Pucelle

Se ha incorporado en esta rama una **copia de solo consulta** de [36 términos investigados en La Pucelle](referencias/la_pucelle/terminos_investigados.csv), junto con los [criterios transferibles de estilo](docs/ESTILO_COMPARTIDO_LA_PUCELLE.md) y un [auditor reproducible](tools/auditar_referencia_la_pucelle.py). La comparación de los 36 términos con los 67 del glosario de Cladun no encontró coincidencias exactas de términos fuente y no modificó ninguna traducción. El objetivo es mejorar la revisión narrativa sin mezclar el universo, las mecánicas o los nombres de los dos juegos.
