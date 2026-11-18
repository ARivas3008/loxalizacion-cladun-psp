# Reinserción sin desplazar recursos — protocolo de seguridad obligatorio

**Estado: protección binaria demostrada en modificaciones pequeñas. Reinserción completa y prueba visual aún pendientes.**

## Objetivo

No se permitirá que traducir un diálogo desplace ni cambie bytes de retratos, sprites, tiles, fuentes, mapas u otros recursos. La validación debe ir más allá de comprobar que la ISO tenga el mismo tamaño.

Cladun PSP dispone de ISO9660 → `PSP_GAME/USRDIR/DATA.DAT` → PSPFS (349 entradas) → DSARC anidados. El verificador guarda para cada comparación los offsets, tamaños, formatos y el contenido exacto de las entradas ajenas al cambio.

## Etapa A: fuente, únicamente

```bash
python tools/font_es_patch.py --iso Cladun-USA.iso --candidate Cladun-Font-Private.iso
python tools/font_es_guard.py --original Cladun-USA.iso --candidate Cladun-Font-Private.iso
```

El verificador exige que todas las demás entradas PSPFS y todos los glifos antiguos sean idénticos. También revisa cada byte ajeno a las franjas nuevas de `FONT.ARC`, sus imágenes, posiciones y punteros.

La copia local de prueba añadió 19 glifos y creció 464 bytes, dejando 32 bytes libres sin cambiar la posición del archivo que sigue. **No se ha comprobado el render de estos glifos en PPSSPP**.

## Etapa B: texto, solo dentro de tramos declarados

Una vez construida y **comprobada** la fuente (por separado), cualquier edición textual crea otra candidata privada. Se compara con la copia de la etapa A, no con una ISO arbitraria.

```bash
python tools/iso_guard_global.py \
  --original Cladun-Font-Private.iso \
  --candidate Cladun-Font-Y-Texto-Private.iso \
  --sha256-original <SHA256_EXACTO_DE_CLADUN_FONT_PRIVATE> \
  --permit SCRIPT.SDT/SCRIPT.DAT:687:19
```

El parámetro `--permit` expresa `PADRE/HIJO:OFFSET_DECODIFICADO:LONGITUD_EN_BYTES`, no una posición física inventada dentro de la ISO. Para la prueba se usó una cadena que empieza en 687 y ocupa 19 bytes en `SCRIPT.SDT/SCRIPT.DAT`.

El proceso rechaza:

1. Modificar tamaños u offsets de ISO9660, PSPFS o DSARC; también rechaza crear o eliminar entradas.
2. Cambiar el método de compresión IMY por GZIP en el recurso objetivo.
3. Modificar bytes fuera de los segmentos de texto expresamente permitidos, aunque la longitud sea igual.
4. Introducir referencias a datos comprimidos que alteren otras cadenas al descomprimir.
5. Tocar FONT.ARC, retratos, tiles o cualquier recurso PSPFS distinto del autorizado.
6. Modificar un campo de longitud fija por encima de su capacidad, o reconstruir punteros de scripts sin ingeniería previa.
7. Cualquier cambio extra de bytes de la ISO fuera de `DATA.DAT`.

**Los cambios de script con distinta longitud no están autorizados.** El verificador de aislamiento no es un inyector y no amplía automáticamente recursos para colocar español más largo.

## Resultado real de la prueba de dos etapas

1. **ISO original → ISO con fuente:** validación de 349 entradas, 348 ajenas idénticas, 19 nuevos glifos; PASS binario.
2. **ISO con fuente → ISO con un byte de diálogo editado:** se modificó un byte decodificado autorizado, manteniendo idénticos los 348 demás recursos, incluida la fuente; PASS binario.
3. **Una copia con alteración extra de FONT.ARC:** RECHAZADA por el verificador textual.
4. **Cuatro corrupciones provocadas en la prueba de fuente:** las cuatro RECHAZADAS.

Informe: [aislamiento combinado](../reports/aislamiento_combinado_es.json).

## Lo que permanece pendiente

- Confirmar que el motor del juego acepta los nuevos códigos PUA y que PPSSPP dibuja bien los 19 glifos.
- Revisar y ajustar textos para sus límites reales de ancho, bytes y punteros.
- Crear un inyector para múltiples registros con rollback y manifiesto de offsets, sin adivinar límites.
- Verificar retratos y tiles por capturas de pantalla, pruebas de menú, mapas y combate en PPSSPP.
- Generar solo un parche diferencial para que cada usuario lo aplique a su propia ISO original, cuando el comportamiento sea satisfactorio.

**Una prueba de bytes idénticos no garantiza por sí sola una representación visual idéntica si el código del motor falla.** Por eso el resultado sigue siendo un prototipo binario, no una versión jugable aprobada.
