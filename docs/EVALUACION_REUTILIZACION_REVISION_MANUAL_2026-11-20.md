# Dictamen de reutilización de `revision-manual-dialogos` (20/11/2026)

**Conclusión: APROVECHABLE COMO BASE LINGÜÍSTICA; NO APROBADO COMO PARCHE JUGABLE.**
Auditoría comparativa de `main`, `revision-manual-dialogos` (442b6c7b) y
`correccion-qa-jugabilidad-ui-20261120`. Este documento no sustituye una
prueba funcional de PPSSPP y no modifica los corpus ni recursos del juego.

## Comprobaciones verificadas

- El corpus original mantiene **9.237 filas, orden, ID, texto fuente,
  origen, `bytes_hex`, `offset_hex` y capacidad** idénticos.
- La revisión manual tiene **910 IDs con un valor español diferente de
  `main`**. Se documentaron **914 intervenciones** (687 + 227);
  intervenciones y entradas distintas son métricas diferentes.
- De los **24 IDs** corregidos en la rama de QA reciente, **solo 2** habían
  sido cambiados por la revisión manual respecto a main (000794, 000795).
  000795 coincide en ambas; **000794 requiere cotejo editorial**. Los otros
  22 no están corregidos en `revision-manual-dialogos` y deben conservarse
  durante la conciliación.
- `qa/INFORME_CIERRE_LINGUISTICO_2026-11-20.json` registra 586 escenas,
  2.216 cajas reconstruidas y 110 decisiones. Son resultados estáticos,
  no prueba humana exhaustiva ni renderizado de todos los textos.
- El workflow de cierre de revisión (run 44814706718) terminó con éxito.
  Su log muestra **100 tests ejecutados, 1 omitido**.
- Inspección byte-a-byte de `bytes_hex` del corpus canónico: **0 usos como
  códigos independientes de `0xA1..0xB3`**. Se observaron **486 usos como
  segundo byte de caracteres Shift-JIS de dos bytes**. Esto respalda el
  aislamiento del nuevo códec de fuente entre los textos recuperados,
  sin garantizar el comportamiento del ejecutable ni recursos no extraídos.
- Con los archivos originales `SCRIPT.DAT` y `SCRIPT.TBL` de la ISO USA
  SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`:
  1.625 scripts, 51.705 comandos, 633.344 bytes de `SCRIPT.DAT`.
  La reconstrucción **sin sustituir textos** recupera los 633.344 bytes
  exactamente. No demuestra equivalencia de saltos cuando cambian longitudes.

## Riesgos sin resolver

1. **Pérdida de correcciones por fusión:** las ramas están divergidas;
   fusionar un CSV completo por sustitución eliminaría cientos de cambios.
   Conciliar por ID, con origen inmutable, preimagen y auditoría de conflictos.
2. **Desborde real de interfaz:** el corpus `revision-manual-dialogos`
   todavía contiene `005687 = Volumen de efectos de sonido`,
   `005688 = Volumen de música de fondo`,
   `005712 = Menos de 10 años`. Corregidos en rama QA, pero sin validación
   de ancho en píxeles de PPSSPP.
3. **Diálogos erróneos:** `000793` todavía dice
   `Me pediste que te cuidara.` pese a que el original inglés se refiere
   a ambos padres. `000799` sigue diciendo
   `Lo quiero para los próximos seis meses.` y rompe la continuidad con
   `000798`. Hay revisión editorial adicional pendiente.
4. **Salto de nivel y enciclopedia:** las longitudes de los comandos
   textuales se reescriben, pero no se ha certificado el efecto en referencias
   internas ni la ejecución de las rutas de progreso. El aislamiento binario
   y las pruebas unitarias no demuestran funcionamiento del intérprete.
5. **Nueva fuente:** `revision-manual-dialogos` introduce fuente de un byte
   `0xA1..0xB3` y reconstrucción de atlas. La documentación v0.1.3 informa
   una prueba parcial de `música` y `configuración` sin espacios incorrectos;
   falta validación de los 19 símbolos en pantallas distintas.
   La rama de QA actual aún usa el códec anterior; seleccionar uno coherente
   al integrar, no mezclar bytes de fuente de un esquema con otro.
6. **Diferencial BPS de procedencia no acreditada hasta nivel CSV:**
   el commit `442b6c7b` incluyó un BPS experimental en
   `patcher/cmd/cladun-patcher/traduccion_es_experimental.bps` y publicó
   un pre-release v0.1.3. El workflow verifica un SHA fijo de BPS
   `300f0eabccf7bf64b2d1eb0e783d31a213f62fdc006ac193fad2918b23e92b80`
   y compila la GUI, **pero no reconstruye ese BPS a partir de la última
   versión del CSV en el mismo workflow** ni acredita por manifiesto que
   contiene cada una de las 914 revisiones.
   El informe de cierre anterior aún dice «parcheador pendiente», mientras
   un commit posterior añadió v0.1.3. No confundir las fechas de esos estados.

## Puerta de aprobación

**NO FUSIONAR COMO PARCHE COMPLETO.** Preparar una rama de conciliación
basada en `revision-manual-dialogos`, transportar las 24 correcciones
por ID y sus pruebas con resolución explícita de 000794, y regenerar todas
las vistas. A continuación: enlazar hash del CSV, código de fuente y
manifiesto de sustituciones al hash del BPS reconstruido desde la ISO
exacta; exigir regresión real en PPSSPP para acceso al segundo nivel,
enciclopedia, menús, cuadros de texto, controles, combate, guardado y
carga antes de un lanzamiento estable.

No subir ni distribuir la ISO original o candidata ni extraer/redistribuir
los assets del juego. Este dictamen distingue QA de texto, verificación
de aislamiento binario y validación funcional.
