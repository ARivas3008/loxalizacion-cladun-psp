# Diagnóstico de bloqueo en «NOW LOADING» — Cladun español, 20/11/2026

## Incidencia confirmada

Un usuario informó que la ISO generada por el parcheador experimental v0.1.1 mostraba «NOW LOADING» indefinidamente. El compilador BPS, el CRC, los hashes y los cotejos de assets ajenos eran correctos, pero **no garantizaban compatibilidad con el cargador gráfico del juego**.

Se reprodujo la incidencia con una ISO USA propia identificada mediante SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, ejecutada en PPSSPP v1.20.4 Linux x86_64 con renderizado por software en una pantalla virtual. La imagen original progresó por la introducción; el parche anterior producía numerosas entradas `GPUCommon CALL to illegal address`.

## Aislamiento y causa

Se probaron cambios independientes:

| Variante | Resultado observado |
| --- | --- |
| ISO USA sin modificar | Introducción y menú originales; sin ese fallo GPU |
| ISO antigua con los cuatro contenedores de texto/gráficos | Error GPU y carga defectuosa |
| Sólo fuente española modificada | Superó la fase inicial, sin fallo GPU |
| `SYS.DAT2` reubicado sin cambios de contenido | Sin el fallo GPU |
| `SYS.DAT2` con PNG modificadas y duplicadas/anexadas al final | Se reproduce el fallo GPU |
| Scripts modificados sin el contenedor gráfico problemático | Avanza al menú sin ese fallo GPU |
| `SYS.DAT2` con reconstrucción compacta | Supera la fase inicial sin ese fallo GPU |
| Versión combinada con reconstrucción compacta | Menú español y configuración inicial de «Comenzar» comprobados |

El método anterior preservaba los bytes originales y **anexaba** las seis PNG traducidas al final de `SYS.DAT2`, aumentando casi al doble el tamaño declarado del archivo. Este método era estructuralmente válido para el lector DSARC del proyecto, pero el motor del juego no lo manejó correctamente. La correlación reproducible con el fallo GPU identifica el **método de empaquetado de SYS.DAT2** como responsable operativo; no se ha demostrado cuál comprobación interna exacta realiza el motor.

## Corrección técnica

`tools/integrar_parche_seguro.py` ahora utiliza `rebuild_sys_arc_compact` para construir una nueva tabla y seis PNG de texto sin conservar copias redundantes. Las imágenes se alinean a 512 bytes. Se comprueba que todo quepa dentro del slot original, sin modificar los offsets de retratos, sprites, mapas y los recursos PSPFS restantes. En particular:

- `SYS.DAT2`: offset PSPFS original y nuevo `3035136`; longitud original `350720`; longitud nueva `351232` bytes, usando exactamente el espacio disponible antes del siguiente recurso.
- `DATABASE.DAT`, `SCRIPT.SDT` y `STAFFROLL.TXT`: permanecen en el esquema append-only con sus tamaños y punteros verificados.
- 9.237 entradas consideradas en el plan; 8.491 sustituciones realizadas, 746 sin cambios, 0 bloqueos estáticos.
- 345 recursos PSPFS fuera de los cuatro contenedores no cambiaron su offset ni sus bytes, según el verificador binario.
- La ISO privada candidata resultó en SHA-256 `27864a48787e54dff7e211214becf26ddbc688a84a1cf78fb444686a8e475f18`.
- El diferencial BPS (`b913cb5509f22721ff533f88848facdc894a3047b66a2597aaa7f333741d69e0`) reconstruye exactamente la candidata sobre la ISO original (verificado con SHA-256 y CRC32).

## Validación y limitaciones

Se verificó en PPSSPP v1.20.4 Linux que la integración compacta llega al menú traducido («Comenzar», «Continuar», «Opciones»), entra en la pantalla inicial de nueva partida y avanza a la introducción tras elegir música de fondo. No se observaron los errores `GPUCommon CALL to illegal address` de la versión anterior durante la prueba combinada. **Se trata de una prueba parcial**, no de la validación de todos los diálogos, creación de personaje, mapas, retratos, combates, guardado o PSP real.

Las 19 letras y signos españoles permanecen en fase experimental: se observó español con acentos en el menú de nueva partida, sin una inspección exhaustiva de las 19 variantes. No afirmar 100 % de compatibilidad jugable ni traducción final. El borrador contiene entradas todavía automáticas y sin revisión narrativa humana.

## Reproducción local sin distribuir material comercial

1. Obtener legítimamente la misma edición USA (comprobar el SHA-256 exacto).
2. Ejecutar `python -m unittest discover -s tests -v`, incluidos `tests/test_sys_compacto.py`.
3. Ejecutar `python tools/integrar_parche_seguro.py --iso ORIGINAL.iso --candidate CANDIDATA_PRIVADA.iso --report informe.json`.
4. Ejecutar `python tools/generar_parche_bps.py --original ORIGINAL.iso --candidato CANDIDATA_PRIVADA.iso --informe-integracion informe.json --salida PARCHE_PRIVADO.bps --informe-bps verificacion.json --experimental`.
5. Comprobar que el BPS reconstruye exactamente el SHA-256 indicado y probar la ISO privada en PPSSPP. No añadir la ISO, BPS, PNG o fuentes comerciales a GitHub.

El parcheador Windows privado v0.1.2 incorpora ese BPS y solicita solo la ISO original. La versión v0.1.1 debe descartarse. El repositorio público contiene fuentes y comprobaciones, no la ISO candidata ni el BPS privado.
