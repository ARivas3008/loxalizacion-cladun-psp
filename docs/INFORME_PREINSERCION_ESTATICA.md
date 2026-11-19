# Auditoría estática de preinserción y seguridad de recursos — Cladun PSP (USA)

**Fecha:** 18 de noviembre de 2026. **Estado: análisis estático documentado; NO autorizado para parche final ni reinserción masiva.**

## Resultado reproducido por GitHub Actions

Se analizaron **9.237 unidades** de `corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv` frente al borrador español `traduccion/CLADUN_BORRADOR_ES.csv`. Se preservaron identificadores, originales, bytes fuente, orígenes, offsets y marcadores. La ejecución [44425291807](https://github.com/ARivas3008/loxalizacion-cladun-psp/actions/runs/44425291807) completó satisfactoriamente **31 pruebas**, con una omitida por requerir una ISO privada. El propio workflow genera un CSV por unidad y un JSON resumen como artefactos temporales.

| Diagnóstico de bloqueo o estado | Registros |
| --- | ---: |
| Cambio de longitud de texto dentro de scripts (no se reconstruyen punteros) | 4.576 |
| Traducción que excede el campo fijo, incluido NUL | 280 |
| No se ha demostrado la capacidad del campo | 816 |
| Rótulos que se encuentran en imágenes | 6 |
| Campo fuente incompleto, sin traducción | 2 |
| **Solo candidata para ensayos adicionales, no validada en el juego** | **3.557** |
| **TOTAL** | **9.237** |

**Entradas con autorización para inserción definitiva: 0.** Es correcto que el escáner rechace las 5.680 restantes. Ajustar frases por longitud sin contexto no es una solución global; el juego requiere estudiar punteros, instrucciones y su espacio real.

## Prevención de corrupción de retratos, sprites y tiles

La jerarquía analizada es ISO9660 → DATA.DAT / PSPFS (**349 recursos**) → miembros DSARC. Las herramientas de verificación ya incluidas hacen comprobaciones independientes de fuente y de tramos textuales:

- `tools/font_es_guard.py` compara los **2.721 registros existentes** de la fuente, el atlas anterior, el índice y los **348 recursos PSPFS ajenos**, e impide alterar bytes fuera de la ampliación autorizada de FONT.ARC.
- `tools/iso_guard_global.py` compara tamaño, estructura, offsets, métodos de compresión y bytes sin permiso. Solo acepta tramos decodificados de **igual longitud**, definidos expresamente. Comprueba los demás miembros DSARC y los demás recursos PSPFS e ISO9660.
- `tools/auditar_preinsercion_es.py` **no inserta nada**; evita iniciar una inserción claramente fuera de capacidad, con marcadores alterados o texto no reversible. La clasificación de «candidato» no es permiso de escritura.

Una prueba anterior de dos etapas aisló la ampliación experimental de FONT.ARC y un cambio de un byte en SCRIPT.DAT; informes: [fuente](../reports/fuente_es_19_glifos.json) y [aislamiento](../reports/aislamiento_combinado_es.json). **No demuestra que 4.576 scripts con aumento de bytes puedan escribirse, que el cargador los interprete o que los retratos se vean correctamente.** El bloqueo continuará hasta que existan pruebas de ejecución.

## Alfabeto español y codificación

`tools/charset_es.py` define 19 glifos españoles con CP932 privado reversible **F5A0–F5B2**. `tools/font_es_patch.py` genera una fuente **experimental** que preserva los glifos anteriores en sus posiciones y aprovecha espacio reservado. No se ha validado cómo el renderizador PSP lee esos códigos o cómo muestra mayúsculas, signos, selección y saltos en cuadros de texto reales. No usar el mapeo histórico F040–F052.

## Comandos y condiciones de aprobación

```bash
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte reports/preflight_local.json --filas reports/preflight_local.csv
```

Para aprobar **un ensayo binario específico**, debe existir un manifiesto con la huella exacta de la ISO, offsets y miembros de destino, bytes originales y españoles codificados, hash de todos los miembros vecinos, preservación de punteros y formato del empaquetado, comparación byte a byte de los otros recursos, rechazo transaccional si falla una prueba y una prueba real de arranque, menús, escenas, retratos, mapas/tiles y caracteres españoles en PPSSPP. Un **PASS de aislamiento no reemplaza una captura visual ni la verificación del cargador**.

Los informes en el repositorio no distribuyen ninguna ISO, BIN, fuente extraída, atlas ni otros materiales del juego. Los controles actúan sobre copias privadas del propietario y deben fallar ante cualquier anomalía.
