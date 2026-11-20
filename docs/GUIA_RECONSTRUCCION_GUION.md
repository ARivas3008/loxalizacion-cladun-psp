# Guion completo reconstruido de Cladun (USA/PSP)

## Objetivo

La extracción original de 9.237 unidades registra **cada renglón textual por separado**. Este generador toma el original y el borrador español sin modificarlos y reúne **cada cuadro de diálogo** en un párrafo legible, conservando todos los fragmentos y sus IDs. Agrupa los cuadros por escena y separa las decisiones del jugador. Los nombres explícitos `personaje_interlocutor` (`0x6E`) se asocian **solo al cuadro próximo**. Donde no hay evidencia suficiente aparece **HABLANTE NO VERIFICADO**: un guion sin nombres inventados es preferible a un guion con atribuciones erróneas.

> No confundir la *caja de diálogo reconstruida* con un turno narrativo completo de un personaje a lo largo de varias cajas. Entre cajas puede haber cambios de interlocutor ejecutados por instrucciones no incluidas en el corpus. El programa **no** fusiona esas cajas a ciegas. El archivo incluye la escena entera, con todas las cajas sucesivas, para facilitar esa revisión humana.

## Archivos publicados automáticamente

| Archivo | Uso |
|---|---|
| `lectura/CLADUN_GUION_RECONSTRUIDO_LECTURA_ES.txt` | Guion íntegro **en español**, por escena y hablante, sin ruido de IDs. Es la lectura más sencilla para detectar frases poco naturales. |
| `lectura/CLADUN_GUION_RECONSTRUIDO_COTEJO_ES_EN.txt` | El mismo guion **bilingüe**, con cada cuadro reconstruido, sus IDs exactos y alertas. |
| `lectura/CLADUN_TODO_TEXTO_RECONSTRUIDO_ES_EN.txt` | Guion bilingüe y, después, todos los textos ajenos a scripts (nombres, objetos, interfaz, créditos y rótulos), por recurso y registro: **9.237 unidades, sin omisiones**. |
| `lectura/CLADUN_MAPA_DE_DIALOGOS_RECONSTRUIDOS.csv` | Mapa editable para seguimiento: cuadro, IDs, original/español completos, hablante, atribución y columnas vacías `propuesta_es` y `nota_editorial`. **No** es formato de reinserción directa. |
| `lectura/CLADUN_ALERTAS_RECONSTRUCCION.csv` | Lista de indicios de puntuación introducida entre fragmentos, nombres propios posiblemente traducidos y textos sin traducción. Son **alertas**, no sentencias definitivas. |
| `lectura/CLADUN_RESUMEN_RECONSTRUCCION.json` | Conteos, hashes, método y límites de la reconstrucción. |

## Ejemplo: por qué es necesario reconstruir

Las filas separadas del CSV dicen:

- EN: `I'm Crosstine, and I come` → ES: `Soy Crosstine y vengo.`
- EN: `from a noble bloodline.` → ES: `de linaje noble.`

En el nuevo guion queda **completo**:

**Crosstine**: `Soy Crosstine y vengo. de linaje noble.`

**Original completo**: `I'm Crosstine, and I come from a noble bloodline.`

La lectura entera revela el punto mal colocado. El script detecta y marca esta anomalía; **no** la arregla solo, porque unificar y volver a dividir líneas exige validar el cuadro en PPSSPP.

Otro ejemplo de una misma caja:

**Joven frenético**: `¡No te vayas así sin más! ¿Estás cansado? ¿Te duele algo? ¡Mírate! ¡Estás cubierto de barro!`

**IDs**: `CLD-000804`, `CLD-000805`, `CLD-000806`. Es **una intervención completa**, no tres traducciones sin contexto.

## Método para corregir un diálogo

1. Abre `CLADUN_GUION_RECONSTRUIDO_LECTURA_ES.txt` y lee cada escena como si fuera un guion. Si detectas una frase extraña, localízala en `CLADUN_GUION_RECONSTRUIDO_COTEJO_ES_EN.txt` y compárala con el inglés completo.
2. Copia los IDs del cuadro en `CLADUN_MAPA_DE_DIALOGOS_RECONSTRUIDOS.csv`. Si propones una versión más natural de la intervención completa, escríbela en `propuesta_es` y documenta el motivo en `nota_editorial`; **no reemplaces** la columna `espanol_completo` (trazabilidad de origen).
3. Para llevar las correcciones al videojuego, edita **solo la columna `espanol`** de `traduccion/CLADUN_BORRADOR_ES.csv` con `editor/Cladun_Editor_Offline.html`. El segmento original puede ocupar varios IDs: distribuye la traducción corregida en los campos físicos correctos sin mover los datos externos. No lo repartas automáticamente en partes de la misma longitud.
4. Valida el CSV con `python tools/aplicar_correcciones_editor.py --entrada CLADUN_BORRADOR_ES_CORREGIDO.csv`. Aplica con `--aplicar` solo cuando lo apruebes; comprueba tokens/variables, nueva codificación, ancho de caja y visualización de acentos en PPSSPP.
5. Regenera el guion para comprobar que, al unir otra vez, la intervención se lee correctamente.

## Seguridad y límites

- **No se modifican** `grupo_id`, `text_id`, originales, offsets, `bytes_hex`, ISO, gráficos ni glifos.
- Los renglones contiguos (`orden_script` consecutivo) forman la unidad de caja reconstruida. Un salto en la secuencia da **una nueva caja**, excepto cuando **un único comando intermedio** separa una oración inglesa manifiestamente incompleta de su continuación en minúscula. Esta unión excepcional se marca `UNION_ENTRE_CAJAS_POR_ORACION_INCOMPLETA_REVISAR` y requiere aprobación humana. En ningún caso implica atribuir automáticamente la voz anterior.
- La fusión agrega separadores entre fragmentos, pero **no elimina puntuación ni inventa palabras**, para que los errores sigan visibles.
- El orden físico de los bloques no certifica el orden en que el usuario experimenta todas las rutas alternativas del juego.
- Los nombres de pantalla basados en `0x6E` pueden no equivaler a la identidad narrativa definitiva; otras instrucciones del motor controlan cambios de cuadro.
- El nuevo texto plano es **material de revisión**, no un archivo reinsertable. Una buena frase en UTF-8 no demuestra que el códec, la fuente, el ancho o la ejecución de PSP la representen correctamente.

## Regeneración

Desde la raíz de la rama `revision-manual-dialogos`, con Python 3.10 o posterior:

```bash
python tools/reconstruir_guion_completo.py
python -m unittest discover -s tests -p 'test_reconstruir_guion_completo.py' -v
```

GitHub Actions ejecuta estos comandos y actualiza automáticamente los seis ficheros generados en la misma rama. Los archivos originales no se tocan.
