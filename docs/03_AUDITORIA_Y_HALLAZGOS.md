# 03 — Auditoría completa de candidatos previos

**Fecha:** 17 de noviembre de 2026. **Versión analizada:** Cladun USA PSP, volumen `CLASSIC_DUNGEON_TRIAL_AND_APPEND`, hash ISO declarado en README.

## Método ejecutado

Se compararon los registros previos (`corpus/todo_el_texto.csv` de la extracción intermedia) contra el contenido real de `DATABASE.DAT`, descomprimido de la ISO. Por cada tabla de tamaño fijo, se verificaron número de registros, tamaño constante y límites de cada campo textual. Los archivos de nombres directos se validaron con registros de 32 bytes. En `MAHO-JIN.DAT` se verificó la tabla específica de nombres en registros de 32 bytes. Las cadenas del motor se identifican a través de opcodes, pero **no se exportan instrucciones al corpus**.

### Diferencias encontradas

| Hallazgo | Cantidad | Decisión |
| --- | ---: | --- |
| Textos válidos antes omitidos por filtro de longitud o caracteres | **127** | Recuperados con fuente/offset |
| Valores de texto/offset corregidos | **133** | Reconstruidos desde el campo real, manteniendo ID cuando existe |
| Falsos positivos de valores numéricos en `LV.DAT` | **56** | Excluidos |
| Cadenas técnicas `rmap*.dat` | **64** | Excluidas |
| Detecciones erróneas fuera de un campo textual | **32** | Excluidas |
| Líneas de origen vacías | **391** | Excluidas del TXT, registradas en QA |
| Rótulos realmente textuales vistos en seis PNG | **6** | Incluidos |
| Etiquetas con bytes CP932 incompletos | **2** | Incluidas con estado `requiere_reconstruccion` |

Entre las correcciones, los nombres de `DUNGEON.DAT` que figuraban como `eHiyo's Cave` u `oBurning Cave` se reconstruyeron desde el desplazamiento correcto del campo. Otra parte de las correcciones preserva espacios originales de ciertos textos de efectos, que el escaneo heurístico había eliminado mediante `strip()`.

Se recuperaron, entre otros, los textos **`M&S`**, **`Me?`**, **`HP-20%`**, **`LV+`**, nombres japoneses cortos y etiquetas de efectos. `MAHO-JIN.DAT` contenía un falso positivo de datos aleatorios, que fue excluido.

`TIPATTR.DAT` incluye dos campos cuya última secuencia CP932 está incompleta en los bytes fuente. Los valores originales se conservan en `bytes_hex`; la visualización con `�` **no autoriza a completar palabras faltantes**.

## Resultado consolidado

- 9.237 unidades textuales no vacías en el TXT y CSV final.
- 8.202 con estructura de origen identificada.
- 1.033 con uso en juego pendiente de confirmar; dos adicionalmente requieren reconstrucción de bytes.
- 6 rótulos visuales en PNG, incluidos dentro de las 8.202 unidades anteriores.

`qa/decisiones_auditoria.csv` registra cada modificación, recuperación y exclusión. No se han alterado traducciones existentes porque **no hay traducciones todavía**.

## Lo que esta auditoría NO prueba

La clasificación de una cadena como campo textual **no demuestra que aparezca en pantalla**. Por ejemplo, `DIFFICULTY.DAT` y `TIPATTR.DAT` contienen etiquetas japonesas que podrían estar destinadas a depuración; se conservaron en la cola de comprobación en lugar de descartarse o darlas por visibles. Falta también auditar rótulos dentro de ciertos recursos gráficos, fuentes especiales, y cualquier cadena no reconocida del ejecutable. Por tanto no se declara cobertura del 100 % de la versión examinada.
