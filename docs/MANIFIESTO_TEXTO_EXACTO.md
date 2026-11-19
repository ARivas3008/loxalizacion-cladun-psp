# Manifiesto de texto exacto: protección frente a sobrescrituras

**Estado:** herramienta de ensayo estático y binario, todavía NO aprobada como inyector final.

## Problema identificado

La validación anterior de rangos manuales podía autorizar un intervalo de bytes sin demostrar por sí sola que representara un diálogo del corpus. Comprobar offsets y tamaño no sustituye comprobar qué **bytes exactos** se autorizaron. Esto es particularmente delicado en un juego con ISO9660, PSPFS, DSARC, scripts, retratos y tiles.

## Controles añadidos

La nueva herramienta [plan_textual_seguro.py](../tools/plan_textual_seguro.py) y la guarda mejorada [iso_guard_global.py](../tools/iso_guard_global.py):

1. Exigen una huella SHA-256 de la ISO de partida.
2. Comprueban los IDs, el orden y todos los campos inmutables del original frente al borrador.
3. Aceptan exclusivamente entradas clasificadas como candidatas a ensayo estático; NO se convierten en entradas aprobadas para la versión final.
4. Restringen esta fase a campos textuales reales de SCRIPT.SDT/SCRIPT.DAT. No admiten retratos, mapas, tiles, FONT.ARC ni tablas aún no modeladas.
5. Verifican que el original de cada ID coincide byte por byte con SCRIPT.DAT en el offset documentado.
6. Exigen reemplazos distintos y con **idéntica longitud en bytes**, sin rangos superpuestos, y codificación española reversible.
7. Generan un JSON con origen, destino, longitud e identificador. Al validar otra ISO se **recalcula** el manifiesto a partir de la ISO y los CSV, de modo que editar el JSON no sea suficiente para saltarse las protecciones.
8. Comparan los reemplazos **exactos** esperados, incluso dentro de los tramos autorizados, y mantienen todas las comprobaciones de otros miembros DSARC, entradas PSPFS, offsets ISO9660 y bytes no autorizados.

## Prueba privada, sin modificar el juego

Identifique primero un grupo verdaderamente candidato (el ID de abajo es solo un ejemplo y puede estar bloqueado):

~~~bash
python tools/auditar_preinsercion_es.py --reporte preflight.json --filas preflight.csv
python tools/plan_textual_seguro.py --iso Cladun-USA.iso --grupo 000001 --salida plan_privado.json
~~~

Si el grupo elegido cambia de longitud, no coincide con el recurso real o tiene marcadores incorrectos, el segundo comando **debe rechazarlo**.

En una ISO candidata privada creada por una herramienta externa de prueba y sin desplazar recursos:

~~~bash
python tools/iso_guard_global.py --original Cladun-USA.iso --candidate Cladun-Candidato.iso --manifest plan_privado.json
~~~

El comando ya no acepta rangos arbitrarios mediante la opción antigua de permiso manual. Si se usa una ISO con la fuente experimental previamente validada como **original de esta etapa**, generar el plan contra esa misma ISO y proporcionar su SHA-256 exacto con --sha256-iso.

## Limitaciones que siguen vigentes

- Las cadenas de longitud distinta siguen bloqueadas; no existen aún reconstrucción fiable de punteros ni empaquetado masivo.
- El manifiesto no inserta bytes y no permite modificar recursos comerciales.
- Para probar los 19 glifos españoles hace falta comprobar que el motor los acepte y que el atlas se renderice en PPSSPP.
- Deben hacerse pruebas visuales de retratos, menús, mapas, tiles y combate. Un resultado de aislamiento binario no demuestra renderizado correcto.
- Solo se publica código e informes; nunca ISO, fuente, gráficos o paquetes propietarios.
