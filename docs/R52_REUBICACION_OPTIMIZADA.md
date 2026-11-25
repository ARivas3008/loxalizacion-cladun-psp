# R52 — reubicación local optimizada, diagnóstico de los 33 residuales

**No es el perfil conservador oficial.** Se autenticó la ISO privada aportada y se recalculó la asignación de donantes mediante programación dinámica por bloque, priorizando minimizar los comandos no textuales desplazados, después todos los desplazamientos, magnitud de deriva y número de donantes. Se examinó una selección de filas cercanas a los 33 objetivos en los CSV/TSV revisados. La solución no pretende ser óptimo global fuera del conjunto de donantes evaluado. Se conservó la redacción R44 de los residuales; la aprobación editorial final es un control aparte. R52 admite 35 donantes solo si el decodificado exacto de la planificación R43 coincide con el texto del manifiesto. 40 bytes añadidos = 40 retirados; cero uso de padding final.

| Invariante | R44 | R52 |
| --- | ---: | ---: |
| Comandos movidos | 2712 | 146 |
| No textuales movidos | 2221 | 104 |
| Coincidencias numéricas locales LE16 | 81 | 0 |
| Inicios de bloque movidos | 0 | 0 |

La comprobación independiente de la ISO auténtica reprodujo 27 cambios previos (SHA R43 exacto) y 68 R52, **95 cambios escritos**. 51.705 comandos, 46.308 argumentos no textuales byte-exactos, todos los 1.625 inicios y sus 1.625 rellenos finales intactos, SCRIPT.TBL idéntica. Barrido LE16/32 de argumentos no textuales hacia posiciones absolutas y locales desplazadas sin coincidencias. Esto no prueba ausencia de referencias indirectas ni semántica MIPS. Los cambios internos permanecen; la guarda fija debe rechazar el nuevo perfil.

Recompresión selectiva de seis IMY: SCRIPT.SDT 699744 B frente a 699624 B original, cabe en el slot de 699904 B; 160 B libres. La copia diagnóstica en slot fijo mide 305496064 B; reabierta y verificada: 349 offsets PSPFS, otros 348 payloads, metadata ISO9660 intactos. Solo cambia descriptor de longitud SCRIPT.SDT y su slot; SHA en JSON. **No incluye fuente de ligaduras ni demás traducciones acumuladas.** No es una ISO jugable localizada ni se publica.

Se agrega opción `--perfil-total-local-optimizado --acepto-reubicacion-local` al builder acumulado, conservando las opciones anteriores y el bloqueo de exportación BPS. El test de planificación usa el corpus y perfiles reales; la comprobación de la ISO anterior fue una implementación independiente, no ejecución del checkout completo. El perfil fijo sigue 8215/8248, el experimental pretende 8247 sustituciones + 1 sin cambio. No promoción oficial, no PPSSPP ni release. R51 CI 45701442169 SUCCESS. No modificar prólogo gráfico canónico ni traducciones. 
