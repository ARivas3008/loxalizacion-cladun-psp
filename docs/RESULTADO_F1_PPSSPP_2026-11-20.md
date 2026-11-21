# F1: causa del cuadro de Opciones aislada y parche de presentación aplicado (20/11/2026)

**Alcance verificado: recuperación de anchura en PPSSPP 1.20.4, NO certificación de la aventura completa ni de todos los valores del menú.** Evidencia numérica enlazada: [reports/RESULTADOS_F1_PPSSPP_REAL_2026-11-20.json](../reports/RESULTADOS_F1_PPSSPP_REAL_2026-11-20.json).

## Contexto y controles reales

Se utilizó el 7z privado aportado con la ISO USA exacta SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. Se reconstruyó la versión sin arreglos con los scripts de la rama, y dio **exactamente** el SHA histórico v0.1.5 `9be7b07a2c5c8c9026ffd0f829f613237f9a31e8fe2455856649ff6c1fe2b4ef`.

Se ejecutó PPSSPP 1.20.4 oficial, AppImage SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`, software renderer, Xvfb 1280×720, ventana 960×544 a x160/y88. El lanzador extraído usa SDL_AUDIODRIVER=dummy (PulseAudio no disponible). Se accedió realmente a Opciones mediante Return, Down, z y se conservaron capturas PNG crudas de scrot. No se suben imágenes del juego a GitHub; se entregaron como ZIP privado al usuario.

### Medidas verificables sobre capturas reales

En cada PNG se detecta la línea horizontal clara que delimita el borde superior de Opciones, fila y=106, x=160..1104. La longitud del tramo (RGB>125 en los tres canales) es el ancho interior; sumar 8px para el borde exterior aproximado. En los cinco casos el extremo derecho está en x1097.

| Compilación | Izquierda del borde | Interior | Exterior aprox. | Resultado |
|---|---:|---:|---:|---|
| Original USA | 342 | 756 px | 764 px | Sin colisiones |
| v0.1.5 exacta | 774 | 324 px | 332 px | Superposición grave |
| Solo 005697 | 774 | 324 px | 332 px | No repara |
| Solo 005709 | 358 | 740 px | 748 px | Opciones legible |
| Cinco IDs juntos | 358 | 740 px | 748 px | Igual que solo 005709 |

Esta prueba positiva/negativa demuestra que **el relleno final eliminado al traducir el ID 005709** («Show decimal points for damage　　　　　　　» / «Decimales de daño») interviene directamente en el cálculo de anchura de la ventana. No es necesario cambiar el prefijo de %2d ni otros cuatro IDs para recuperar esa anchura. El ancho residual difiere 16px del original: no se ha demostrado cómo elimina el motor ese último bloque.

Se probaron ayudas, movimiento del cursor y la entrada a **Controles** en la variante 005709. Esta pantalla muestra iconos de botones, pero NO certifica todos los accesos al atlas en otros contextos.

## Implementación mínima versionada

- `tools/menu_layout_es.py`: protege el ID, recurso, texto inglés exacto y texto español original; cambia **solo la representación empaquetada del ID 005709** a «Decimales de daño» seguido de diez espacios ideográficos y seis espacios ASCII. Conserva «Decimales de daño» sin relleno invisible en el borrador y en los TXT literarios. Falla si cambian los bytes/ID/preimagen.
- `tools/integrar_parche_seguro.py`: aplica el ajuste al empaquetar el borrador y fuente **canónicos**, no cuando se especifica un `--borrador` experimental. Sigue protegido por `--event-safe-only`, guardas de campos y verificación de 349 recursos PSPFS.
- `tests/test_menu_layout_es.py`: verifica que las 9.237 entradas están intactas salvo 005709.espanol en memoria, que se mantiene el avance FONT.BIN del original y que no cambia ninguna otra sustitución binaria.

La candidata compilada desde el código nuevo y el borrador canónico es **idéntica byte por byte** a `solo-005709.iso`, la candidata observada en PPSSPP. SHA ISO `9b7fc809bb106953a91d6ad6e4e23363eb7fb92760659607d484f71132b5da89`; BPS `5047fa7b565f84ec204f7f1dde4e47752eb2013af8daa40d68714ca7255b1566`. El roundtrip BPS verifica el mismo SHA objetivo.

Las guardas certifican integridad estática: 349 registros PSPFS; 345 recursos ajenos a cuatro contenedores preservados; resto de ISO9660 protegido; 51.705 comandos, 46.308 no textuales, 1.625 comienzos de script y cero offsets desplazados. Se mantienen **4.524 traducciones de script aplazadas**. No inferir de ello que todos los eventos funcionan en el intérprete.

GitHub Actions (commit de tests `24ecc52a6565bd8ef29aa019c2e7c2a8848fec80`, ejecución `44864818033`): **126 tests Python**, Go test, integridad y build Windows sin payload en verde. Además, reconstrucción privada ISO/BPS desde los mismos scripts y prueba PPSSPP real.

## Defectos pendientes y por qué F1 no está cerrada completamente

1. El cuadro reparado mide 748px exteriores, **16px menos** que el USA (764px), aunque en esta pantalla no se observaron solapes tras la corrección.
2. El valor del ID `005710` aparece como **«EN»** para ON y debe revisarse semánticamente, manteniendo la separación entre diseño e idioma; `005713` «APAGADO» y las opciones ON/OFF precisan QA de cada valor.
3. Falta cubrir todas las variantes de control, cursor, opciones y retorno. Se observó el submenú de Controles, no toda la funcionalidad de iconos ni sus índices físicos.
4. Un ensayo adicional de +1 espacio ideográfico en 005709 produjo ISO/BPS binariamente válidos (ISO `f97fa355fce8d7ab55a81fc711e944185ebdce4a320a5077695cb445acd303c8`), pero no se consiguió una captura utilizable de Opciones en PPSSPP; **NO se adoptó**. No cambiar layout por una predicción de 16px.
5. F2 símbolos/atlas, F3 inglés en la introducción, F4 scripts de distinto tamaño, F5 aventura y F6 EXE privado siguen sin aprobación.

## Reproducción y siguientes pruebas

~~~bash
git switch integracion-eventos-segura-20261120
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f1-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f1-integrabilidad.json
(cd patcher && go test ./...)
export ISO_ORIGINAL='/ruta/privada/Cladun_USA_original.iso'
sha256sum "$ISO_ORIGINAL"
python tools/integrar_parche_seguro.py --iso "$ISO_ORIGINAL" \
  --candidate /ruta/privada/Cladun-ES-F1-EXP.iso \
  --report /ruta/privada/F1-integracion.json --experimental-parcial --event-safe-only
python tools/generar_parche_bps.py --original "$ISO_ORIGINAL" \
  --candidato /ruta/privada/Cladun-ES-F1-EXP.iso \
  --informe-integracion /ruta/privada/F1-integracion.json \
  --salida /ruta/privada/Cladun-ES-F1-EXP.bps \
  --informe-bps /ruta/privada/F1-bps.json --experimental --event-safe-only
sha256sum /ruta/privada/Cladun-ES-F1-EXP.*
~~~

**Siguiente experimento concreto:** aislar cuantización del ancho de Opciones (16px residuales), comparar el control original, F1-748 y el ensayo +1 espacio que aún carece de captura, y probar valores de `005710/005713` con cursor/ayuda real, manteniendo `--event-safe-only`. No cerrar F1 hasta que la mejora visual y las opciones completas tengan evidencia. Al terminar actualizar estado y crear **otro** `prompts/SIGUIENTE_TAREA.md` autónomo, que a su vez obligue a generar el siguiente.
