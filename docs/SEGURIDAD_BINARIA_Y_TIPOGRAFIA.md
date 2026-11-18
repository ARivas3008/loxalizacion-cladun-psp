# Cladun PSP — seguridad binaria, codificación y fuentes (18/11/2026)

## Resultado comprobado

Se analizó la ISO USA aportada (SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`; **305.496.064 bytes**). Se hizo un ensayo privado de edición de **dos entradas concretas** dentro de `PSP_GAME/USRDIR/DATA.DAT`: un texto en `SCRIPT.SDT/SCRIPT.DAT` con exactamente **19 bytes antes y después**, y un nombre en `DATABASE.DAT/ARTIFACT.DAT`, con **12 bytes nuevos en un campo de 24 bytes**.

Para cada contenedor se modificó solo su miembro relevante, se recomprimió en una longitud inferior al espacio ya asignado y se actualizó exclusivamente el campo de longitud almacenada de ese recurso. No se desplazó ningún offset del índice PSPFS ni cambió el tamaño total de la ISO. En la prueba se verificó:

| Invariante | Evidencia |
|---|---|
| Tamaño ISO sin cambio | PASS |
| Offsets de **349** archivos PSPFS sin cambio | PASS |
| **347** recursos PSPFS diferentes de SCRIPT.SDT / DATABASE.DAT byte por byte idénticos | PASS |
| Otros miembros de SCRIPT.SDT | **3** intactos |
| Otros miembros de DATABASE.DAT | **29** intactos |
| Archivos ISO9660 distintos de DATA.DAT | **11** intactos |
| `FONT.ARC` y sus atlas | Intactos |
| Todos los bytes cambiados dentro de los dos slots comprimidos y los metadatos autorizados | PASS |
| Arranque, retratos y tiles renderizados en PPSSPP | **NO VERIFICADO** |

**Importante:** recomprimir un archivo binario cambia numerosos bytes dentro de **ese mismo slot**, no solo los caracteres del diálogo. En el ensayo cambiaron 429.561 bytes, todos dentro de los rangos permitidos. Eso **no** afecta los bytes de otros recursos ni desplaza sus posiciones. El intérprete del juego aún debe comprobarse: otros recursos del mismo PSPFS utilizan una envoltura GZIP de 12 bytes, pero no está demostrado que estas dos entradas se puedan cargar con GZIP en tiempo de ejecución.

### Herramienta reproducible

`python tools/reinsercion_segura_demo.py --iso /ruta/a/Cladun.iso --salida resultado.json`

No almacena ni publica ISO comercial, borra su copia temporal y **rechaza**: SHA-256 incorrecto, texto original distinto del esperado, cambio de longitud de instrucción de script, campo DB desbordado, slot comprimido mayor que el original, movimiento de recursos o cualquier byte modificado fuera de los rangos permitidos.

No es un inyector de todo el corpus. Aún no reconstruye scripts variables, punteros de `STRTBL.DAT`, menús de capacidad desconocida ni rótulos gráficos de `SYS.DAT2`.

## Auditoría real de FONT.ARC

Se encontró `FONT.ARC` (un contenedor DSARCIDX) con **FONT.BIN**, una tabla de **2.721** registros de cuatro bytes cada uno y **seis** imágenes `FONT_00.IMY` a `FONT_05.IMY`. Los atlas son texturas IMY de tipo `0xA4`; no se ha demostrado su reempaquetado seguro.

- Los glifos ASCII imprimibles están en FONT.BIN.
- `áéíóúÁÉÍÓÚñÑüÜ¿¡` no son codificables directamente por CP932 ni se encuentran con esos códigos en la tabla original.
- De los 2.721 códigos de FONT.BIN, 2.232 **no aparecen en los textos extraídos**. Esto NO garantiza que sean prescindibles: otros subsistemas pueden usarlos.
- Hay caracteres raros del original codificables por CP932 cuya entrada tampoco aparece en esa tabla; no se debe adivinar cómo los renderiza el juego.

### Adaptación de bytes realizada, atlas pendiente

`tools/charset_es.py` implementa un mapa reversible de **19 caracteres** a `U+E000…U+E012`, que CP932 codifica como `F040…F052`. La codificación y su reversibilidad se probaron. Incluye las letras y signos españoles habituales, más `«`, `»` y `ō` presentes en el borrador. Ninguno de los 19 códigos `F040…F052` ocupa una entrada existente en FONT.BIN, pero **tampoco hay aún imágenes de esos glifos**. Esto no basta para mostrar correctamente español en PSP.

Un modo ASCII de diagnóstico puede generar texto sin tildes para probar el flujo del motor; **no se publica como traducción definitiva**. No se ha tocado FONT.ARC ni se han sustituido glifos japoneses. Una fuente completa requiere reconstruir la asignación de atlas, dibujar glifos, actualizar los códigos y métricas, reempaquetar las páginas sin alterar vecinos y validar su render en PPSSPP.

## Reglas innegociables para toda futura reinserción

1. Guardar hash SHA-256 de la ISO fuente y cotejar cada bytes del texto antiguo antes de escribir.
2. No variar el tamaño de instrucciones de script hasta demostrar y reconstruir todas las referencias a posiciones; el ensayo actual exige exactamente el mismo número de bytes.
3. En campos de base de datos, no superar la capacidad real e incluir un NUL; nunca escribir fuera de su intervalo.
4. No editar punteros, índices o offsets de archivos vecinos ni agrandar un slot comprimido. Si no cabe, **detenerse**; no mover tiles, sprites ni retratos.
5. Verificar que los 349 offsets PSPFS sean idénticos, los demás 347 recursos completos mantengan SHA-256 y todos los miembros DSARC no intervenidos coincidan byte por byte.
6. Conservar valores de formato y marcadores (`%02d`, `%s`, `⑨`, etc.); no aceptar líneas con caracteres no codificables o sin glifo demostrado.
7. Comparar imágenes, fuentes, retratos, animaciones y tiles por hash de archivos y, más adelante, por pruebas visuales/capturas de PPSSPP.
8. Entregar un **parche diferencial** contra la ISO legítima, nunca publicar la ISO, sprites, fonts ni otros recursos comerciales.

## Revisión lingüística

El borrador actual mantiene 9.237 IDs y 9.235 entradas con español. En esta etapa se corrigieron **130** entradas adicionales, principalmente: Pudding (no Pudín), personajes de apoyo (no submarinos), bastón (no personal), Widen (no Ensanchar), Círculo mágico, cambiar de clase y errores de tutorial. En total **196 entradas** están posteditadas/normalizadas por IA. Otras **9.039 entradas con borrador** requieren revisión individual de naturalidad, personaje y contexto. Hay dos registros de fuente CP932 incompleta. Se consolidó el glosario en `docs/GLOSARIO_CANONICO.md`; no significa que el corpus sea perfecto ni esté listo para inserción.

## Lo que aún NO puede afirmarse

- No hay fuente española rasterizada ni parche de glifos verificado.
- No hay inyección validada de los 9.235 textos.
- No se ha probado la carga de GZIP en estas dos entradas por el juego.
- No hay prueba de PPSSPP, hardware PSP ni comparación de capturas.
- Por tanto, **no se puede garantizar al 100 % que retratos o tiles rendericen igual tras un parche general**, aunque el ensayo binario aislado sí mostró que sus archivos no fueron modificados.

Referencias de ingeniería y QA: [PPSSPP: reemplazo de texturas](https://www.ppsspp.org/docs/reference/texture-replacement/), [PPSSPP: fuentes del PSP](https://www.ppsspp.org/docs/getting-started/using-original-fonts/) y [guía de ROMhacking PSP](https://romhackplaza.org/documents/romhacking-psp_basics/). Son referencias generales: **FONT.ARC es específico de Cladun**.
