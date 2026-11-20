# Ensayo privado de parcheador ISO única — 20/11/2026

Este informe distingue claramente **aislamiento binario** de **funcionamiento validado en PPSSPP**.

## Resultados reproducibles en ISO USA auditada

- SHA-256 ISO original: `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- SHA-256 ISO candidata: `ed9a7a41eec842251f618d292c84cfd0a8c892f1fa31aae7d10d920f3edefb84`.
- Unidades del corpus: **9.237**. Inserciones planificadas y ejecutadas: **8.491**. Traducciones que no cambian los bytes: **746**. Bloqueos estáticos de esta ejecución: **0**.
- Recursos PSPFS ajenos a los cuatro contenedores editados: **345**, con contenido y desplazamiento inalterados; el atlas de fuente experimental `FONT.ARC` se cotejó por separado.
- Dos límites estructurales del corpus eran mayores que las regiones NUL reales: IDs `007892` (`MONSTER.DAT`) y `008402` (`RMAPSET2.DAT`). Se añadieron adaptaciones explícitas de inserción con el borrador literario intacto. Otras entradas de base de datos tenían un terminador NUL más corto que el margen modelado; ahora se limita cada escritura a la región de NULs realmente verificada. Los campos de ancho fijo sin NUL solo reciben ediciones dentro de los mismos bytes.
- Se corrigió una comprobación excesiva de directorios ISO9660: al aumentar `DATA.DAT` es legítimo que cambien *exclusivamente* sus ocho bytes de tamaño LE/BE dentro del directorio `PSP_GAME/USRDIR`. Todo el resto del directorio debe permanecer idéntico.
- El BPS privado es de 1.876.021 bytes. SHA-256: `49a2cdf36cb5963a966a29a24da8c5316912c8cd61abebaf8b31b2e42f0c0205`. La reconstrucción de BPS y la prueba independiente con el motor Go recuperaron **exactamente** el SHA-256 de la candidata. Los CRC del formato coinciden.
- Se corrigió un error histórico de constante Go: el antiguo parcheador contenía un SHA-256 con **62 caracteres** en lugar de los **64** del original; por eso v0.1.0 no habría aceptado la ISO USA auténtica. Existe una prueba de regresión.

## Restricciones y pendientes

- **PPSSPP no probado**: arranque, textos, glifos españoles, retratos, animaciones, mapas, combate, saltos del intérprete, espacio de cuadros de diálogo y fuentes.
- BPS español y ejecutable privado experimental **no aprobados para distribución final** ni incluidos en el repositorio público; solo fuente y controles de calidad.
- El aplicador integrado verifica fuente, integridad del BPS y SHA-256 objetivo antes de publicar la salida. La ISO fuente jamás se sobrescribe.

El estado de esta fase es **`EXPERIMENTAL_AISLAMIENTO_BINARIO_SOLAMENTE`**, no `JUGABLE_VALIDADO`.
