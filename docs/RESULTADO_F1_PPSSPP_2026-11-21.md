# F1 Opciones — CIERRE VERIFICADO EN PPSSPP REAL (21/11/2026)

**Dictamen:** F1 cerrada **solamente para la ventana Opciones, sus valores, ayudas y navegación/regreso**. La localización completa NO está finalizada. F2 símbolos/atlas, F3 intro inglés, F4 4.524 scripts, F5 gameplay y F6 entrega final permanecen abiertos. PR #7 sigue en borrador.

## Entorno y autenticación

- ISO comercial USA privada legalmente aportada: 305.496.064 bytes; SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- PPSSPP **real**, AppImage oficial Linux x86_64 1.20.4 SHA-256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. AppImage sin alterar; extraído para entorno aislado. En .env **local** se eligió `SDL_AUDIODRIVER=dummy` en vez de pulseaudio, sin alterar binario.
- Xvfb 1280×720×24, ventana 960×544 en (160,88), software renderer / llvmpipe, entradas Return/Down/z y teclas reales enviadas a Xvfb con XTest/pyautogui; PNG crudos capturados con **scrot** y medidos sin retocar.

## Comparación REAL desde PNG (mismo umbral y resolución)

Método exacto: segmento horizontal continuo más largo con RGB de los tres canales mayor de 125, fila y=106, x=160..1104; se suman **8px aproximados** de marcos al interior para exterior. No confundir tipografía (avance de FONT.BIN) con anchura real de ventana.

| ISO | x inicial | x final | Interior | Exterior estimado | Veredicto |
|---|---:|---:|---:|---:|---|
| Original USA **repetida** en esta sesión, dos PNG | 342 | 1097 | **756 px** | **764 px** | Control positivo |
| 005709 +1 ideográfico U+3000, dos PNG | 326 | 1097 | **772 px** | **780 px** | **Rechazada: 16px demasiado ancha** |
| Solo 005709 +1 espacio ASCII, PNG real | 342 | 1097 | **756 px** | **764 px** | Anchura exacta |
| **Canónica española** +1 ASCII + Sí/No, 18 PNG medibles | 342 | 1097 | **756 px** | **764 px** | **PASS anchura exacta** |

La variante mínima previa (10 ideográficos + 6 ASCII) era 740/≈748px en captura histórica del 20/11; el +1 U+3000 suma 15px de *avance de glifo* pero provoca salto de 32px en tamaño del cuadro, mientras añadir solo un ASCII logra +16px. Esto indica que la rutina de ventanas cuantiza el ancho; **no se ha desensamblado la función exacta**, así que no atribuirle una fórmula no demostrada.

### Corpus y presentación

- ID `005709`: redacción literal **«Decimales de daño»**, presentada con **10 espacios ideográficos + 7 ASCII** al empaquetar canónico.
- ID `005710`: español literal **«          Sí»**, anterior **«          EN»**, conserva sangría de 10 ASCII.
- ID `005713`: español literal **«         No»**, anterior **«         APAGADO»**, al empaquetar agrega **1 ASCII al final** para igualar 84px de avance de «         OFF».
- `005711`/ `005712` («Menos de 1: SÍ», «Menos de 10: SÍ») permanecen intactos. Los cuatro estados de daño decimal se recorrieron en PPSSPP y se observaron dentro del ancho de la caja.
- Se aplicó `tools/aplicar_correcciones_editor.py` mediante el commit **a94e695c2e2380673e915c8068164b8ce2eb6e58**: CSV, ambos TXT, bitácora de dos antes/después y vista total derivados **en un solo commit**. El guion de scripts y auditoría de hablantes no cambiaron porque los dos IDs son de DATABASE.DAT/STRTBL.DAT y no están en SCRIPT.DAT.
- `tools/menu_layout_es.py` y `tools/integrar_parche_seguro.py` tienen preimagen estricta por ID, bytes, recurso, redacción y se aplican **solo a fuente y borrador canónicos**, no a `--borrador` experimental.

## ISO/BPS privadas: tres experimentos con controles estrictos

| Variante | ISO SHA-256 | BPS SHA-256 | Estado |
|---|---|---|---|
| +1 U+3000, NO adoptada | `f97fa355fce8d7ab55a81fc711e944185ebdce4a320a5077695cb445acd303c8` | `279bd99d7a0cfb87fd1bb4a03ee67ecc250d51563e14f12e213283922a8634fc` | BPS exacto; ancho excedido |
| +1 ASCII sola | `2f781c94b3ea835bd317d741793d0e3ed8ec9626dc2ab43a7ee501231e0b1edd` | `96db2092c14c8c854db93d3f27b6c219e698cc22c2e6947dbddfc5c4dcbbc79b` | BPS exacto; 764px |
| **Canónica +1 ASCII + Sí/No** | `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986` | `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd` | **BPS exacto, 764px, valores navegables** |

El integrador **canónico actual** reconstruyó ISO y BPS idénticos byte a byte a la variante combinada probada en PPSSPP, con hashes exactos anteriores.

Comprobaciones binarias nuevas de **candidata y BPS**, no solo de original: 349 PSPFS, **345 vecinos ajenos a cuatro contenedores textuales exactos**, demás archivos ISO9660 intactos, DSARC protegidos, 51.705 comandos, 46.308 no textuales exactos, 1.625 inicios de scripts, **cero** offsets desplazados, 3.724 sustituciones aceptadas, **4.524 traducciones script aplazadas**. BPS reaplicado al original con SHA ISO reconstruida idéntica. Comandos siempre `--experimental-parcial --event-safe-only` y BPS `--experimental --event-safe-only`. Esto NO demuestra funcionamiento de todos los saltos del intérprete.

## QA funcional y capturas PRIVADAS

- Se comprobaron **volumen de efectos y música**, incremento/disminución, tipo musical Real/Retro, las **cuatro** posiciones de visualización de decimales («Sí», «Menos de 1: SÍ», «Menos de 10: SÍ», «No»), efectos de círculo, Capturas y entrada a Controles.
- Se verificó la pantalla Controles con iconos L/R, cuadrado, círculo, cruz y triángulo visibles; se restauró la configuración «Por defecto», se eligió «Fin» y se regresó a Opciones y al título. **No** se demostró si los símbolos se acceden por código o índice físico del atlas desplazado +19; sigue F2.
- **27 PNG verdaderos** (sin ediciones) con SHA256 individual en manifiesto privado, 2 estados del original, 2 del experimento rechazado, 18 estados Opciones de la canónica, varios de Controles y el título; un ZIP privado con informe de medidas y logs. `Cladun_ES_F1_PPSSPP_real_2026-11-21_EVIDENCIAS_PRIVADAS.zip`: SHA `66f23bd7aa08301f652292ca2fc81440cd004403eb613f3ef9b0a1e6f4d66c24`, tamaño **1.202.413 bytes**. **No subir ni capturas ni ZIP a GitHub**.
- PNG autenticados destacables por SHA: USA Opciones `b491a3fba90ca347770c33a6256ce57e9a1e269aac779c5186fecb6c8cfcbefe`; canónica Opciones `5ff7600a3f4423f03a3db7f75e1b6064bf5621ccfaccf61214eba7ccb630915c`; Controles restablecidos `32f53206110b0bfcc331c67a46508c68b6c1a2c481c69810d2d2214d3a6f2750`. La herramienta `tools/medir_f1_ppsspp.py` solo mide los PNG aportados y NO certifica de forma automática su procedencia; esta sesión sí los generó con PPSSPP real y scrot.

## CI y estado del proyecto

Se ejecutaron en sesión Python de pruebas y verificadores de integridad y planificación; Go `go test ./...` PASS. Una ejecución de prueba local en un checkout parcial carecía de `referencias/la_pucelle/terminos_investigados.csv` y tuvo 1 error de archivo ausente por el paquete de fuentes temporal, **no un fallo funcional del parche**; la suite GitHub Actions con checkout completo y Pillow debe ser autoridad para la aprobación de tests al commit final, comprobar CI después de cada escritura.

**F1 Opciones sí está terminada y probada**. Permanece no aprobado el lanzamiento final de la localización, el uso de símbolos fuera de la pantalla revisada, la introducción en inglés, las 4.524 traducciones de SCRIPT.DAT pospuestas y las fases F2–F6. PR #7 continúa en borrador. **Nunca** publicar ISO, BPS ni capturas comerciales a GitHub.

## Relevo recursivo

Ver `prompts/SIGUIENTE_TAREA.md`. La próxima tarea debe comenzar **F2: 19 glifos A1–B3, desplazamiento +19 índices del atlas, botones e interacciones por código versus índice**, conservando congelada la solución F1 y exigiendo otro prompt autónomo al terminar.

## Verificación final de GitHub Actions (21/11/2026)

Las ejecuciones `44956876063` y `44956870486` del commit `88edf04a4667289e45d725828e4c74efd19b1507` resultaron **SUCCESS**. El log registra **140 pruebas Python**, integridad de corpus y borrador, integrabilidad, `go test ./...` y compilación pública Windows x64 SIN payload; prohibición de versionar ISO/BPS verificada. Esto es CI de código; la QA visual/ISO/BPS privada está documentada por separado. Esta incorporación documental da lugar a un HEAD nuevo que debe cotejarse nuevamente antes de declarar CI del HEAD actual.
