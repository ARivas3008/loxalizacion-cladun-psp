# CLADUN ES — R25: objetivo de segundo avance de +20 puntos en ROMhacking

**Corte:** 24/11/2026. **Estado técnico: preparado y probado estáticamente; piloto completo A/C todavía NO ejecutado.** Esta distinción impide confundir una propuesta de sustitución con el porcentaje de juego efectivamente traducido.

## 1. Meta cuantificada y regla de aceptación

| Nivel | Registros | Denominador | Cobertura |
|---|---:|---:|---:|
| **Histórico oficialmente integrado**, sin cambios | 3.724 | 8.248 | **45,1503 %** |
| R24 piloto binario propuesto, sin aceptación C | 5.374 | 8.248 | 65,1552 % |
| **R25 piloto binario ahora implementado, NO oficial** | **7.024** | **8.248** | **85,1600 %** |
| Pendiente si se validasen realmente las 7.024 | 1.224 | 8.248 | 14,8400 % |

R25 agrega **1.650 propuestas frente al piloto R24**: los **352** textos crecientes todavía disponibles dentro de las 44 ligaduras + **1.298** textos decrecientes bajo la hipótesis visual de rellenar con **1–7 espacios ASCII al final**. En conjunto prepara **3.300 nuevas propuestas** frente a la base 3.724. Ni el 65,15 % ni el 85,16 % deben contarse como nuevos porcentajes oficiales mientras no existan pruebas reales del juego y aceptación editorial.

## 2. Evidencia A: nueva auditoría local de la ISO original

El `.7z` comercial fue proporcionado por el usuario y la ISO original se verificó nuevamente de manera **solo lectura**: SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, 305.496.064 bytes. Inspección independiente de PVD ISO9660, `PSP_GAME/USRDIR/DATA.DAT`, 349 entradas PSPFS y `SCRIPT.SDT` (#231): 8 bloques IMY descomprimidos a 930.304 bytes, cuatro miembros DSARC correctos.

- `SCRIPT.DAT`: 633.344 B; SHA-256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`.
- `SCRIPT.TBL`: 52.016 B; SHA-256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`.
- Se releyeron **1.625 bloques**, **51.705 comandos**, **46.308 instrucciones no textuales**, **5.397 opcodes textuales**; inicio del último script 633.008.
- La ISO fuente se mantuvo byte a byte original, no se generó aquí una ISO combinada; no hay evidencia de PPSSPP C en este relevo.

Persiste el impedimento A de R24: aun recompresando un SCRIPT.SDT intacto, el códec actual produce **700.483 bytes** que no caben en el slot inicial de **699.904 bytes**; por seguridad toda nueva `SCRIPT.SDT` debe reubicarse `append-only` o mejorarse y volver a demostrarse su compresión.

## 3. Evidencia B: integrador real de 7.024 como experimento privado

**Herramienta nueva**: `tools/f4_r25_piloto_85pct.py`, complementada con la corrección de `tools/f4_r24_piloto_1650_ligaduras.py`. Esta última comparaba erróneamente la ISO completa contra la original en la auditoría final, incluso cuando la base contiene `DATABASE.DAT`, `STAFFROLL.TXT` y `SYS.DAT2` legítimamente traducidos. La reparación introdujo `unchanged_resources_against_baseline()`, que compara los 347 recursos **no FONT/no SCRIPT** frente a la base ya traducida; mantiene la auditoría origen→base en el integrador anterior.

### Selección y contrato de bytes

Se reutilizan las **2.002** sustituciones estrictas con 44 ligaduras libres de colisión, sin alterar un solo offset de eventos. Se agregan **1.298** de las **1.345** alternativas de textos más cortos que cumplen los siguientes filtros: bytes fuente originales completamente ASCII imprimibles (sin porcentajes o barras inversas), propuesta española recodificable y reversible, un campo de texto SCRIPT auténtico, sin controles, sin espacio final previo, y diferencia máxima de **7 bytes**. Se eligen primero las de menor relleno y, para empates, menor offset. Total experimental: **3.899 espacios ASCII finales añadidos** a los 1.298 campos; no equivalen a pruebas de visibilidad ni de naturalidad.

**Peligro específico:** un texto con 1–7 espacios finales sigue cabiendo perfectamente en su comando y mantiene los offsets, pero esos espacios podrían mostrarse en el cuadro o provocar wrap, clipping, saltos de línea o deformación del retrato. **No aprobar hasta hacer un A/B/A visual auténtico para cada entrada**. Si falla, no aplicar el relleno como solución final: implementar un códec visualmente neutro contrastado o un esquema de reubicación de instrucciones con referencias MIPS verificadas.

### Pipeline de ISO privada propuesto (implementado, no ejecutado aquí hasta su final)

1. Verificar SHA y geometría de la ISO original; cargar corpus inmutable de 9.237 IDs. Contrastar **cada una** de las 3.300 preimágenes y longitudes contra `SCRIPT.DAT` auténtico, auditar en RAM los 51.705 comandos y los 46.308 no textuales.
2. Construir la base con `tools/integrar_parche_seguro.py`, `experimental_partial=True` y `event_safe_only=True`: **exigir** 3.724 sustituciones y 4.524 diferidas, `SCRIPT.TBL` igual y eventos de offset fijo.
3. Añadir **FONT.ARC 19+44** experimental: 144.000 B dentro del slot de 144.384; validar atlas IMY y 347/348 recursos vecinos, incluyendo el margen retirado de FONT de 19 caracteres. **La alineación interna a 16 B no ha sido aceptada por PPSSPP**.
4. Sustituir los 3.300 campos de mismo ancho en `SCRIPT.DAT` de la **misma base 3.724**; revalidar lista completa de instrucciones, tabla y bytes no textuales.
5. Reempacar IMY con roundtrip y **añadir** `SCRIPT.SDT` al final de DATA.DAT, modificando solo su índice PSPFS, el tamaño de DATA.DAT en ISO9660 y los metadatos de volumen pertinentes; comparar 347 recursos ajenos contra la base traducida.
6. Crear ISO **solo privada y nueva**, sin sobrescribir original. Sin PPSSPP 1.20.4 real, persistir `new_official_integrations=0` y `release_authorized=false`.

### Comandos

```bash
python tools/f4_r25_piloto_85pct.py
python -m unittest discover -s tests -p 'test_f4_r25*' -v
python tools/f4_r24_script_slot_audit.py --iso-original /PRIVADO/Cladun_USA.iso
python tools/f4_r25_piloto_85pct.py \
  --iso-original /PRIVADO/Cladun_USA.iso \
  --candidate /PRIVADO/Cladun_R25_7024_EXPERIMENTAL.iso
python tools/qa_cobertura_4_areas.py --require-closed  # debe rechazar hasta validación real
```

El último comando de generación de ISO combinada **no fue ejecutado aquí** por no disponer de un checkout local completo de los scripts/corpus del repositorio y de PPSSPP oficial en este contenedor. El código sí está en GitHub y sus tests B se ejecutan en CI; la ISO original auténtica fue examinada por separado. No se publican juegos, archivos comerciales, FONT.ARC, BPS o capturas inventadas.

## 4. Trazabilidad editorial y QA

- `traduccion/propuestas/R24_COLA_EDITORIAL_1650.csv` — los primeros 1.650 del piloto anterior.
- `traduccion/propuestas/R25_COLA_EDITORIAL_1298.csv` — los 1.298 casos del relleno ASCII y el número de espacios por entrada.
- **`traduccion/propuestas/R25_COLA_CONJUNTA_3300.csv`** — los 2.002 con ligaduras y 1.298 de relleno, ordenados por offset, con ID, tamaño y método; **3.300 filas**. Ninguna fila incluye diálogos, datos comerciales o falsos resultados: todos `PENDIENTE_CONTEXTUAL / NOT_RUN / NO`.
- `tests/test_f4_r25_piloto_85pct.py` coteja en CI la selección del corpus real y las **3.300** filas de la matriz contra el algoritmo Python, la codificación reversible y el límite máximo de 7 espacios.
- `.github/workflows/validacion-integracion-eventos.yml` ejecuta la planificación B explícita: exige **2.002 + 1.298 = 3.300**, **1.345** candidatas de relleno, **7.024/8.248 = 85,16 % solo como objetivo**, y `new_official_integrations == 0`.
- QA `Q069` (piloto completo) y `Q070` (espacios finales) añadidos como **NOT_RUN**. La matriz alcanza **70 casos definidos** sin nuevos PASS C.

## 5. Decisión

**No incrementar oficialmente** las 3.724 sustituciones ni declarar romhacking 85,16 %. Lo que sí se entregó es una ruta reproducible de código y una matriz concreta de 3.300 registros para probar el salto, con los riesgos cuantificados y un bloqueo de aprobación formal. El relevo recursivo `prompts/SIGUIENTE_TAREA.md` debe ejecutar primero R24/R25 en una misma ISO y solo actualizar los contadores cuando las pruebas C y la revisión editorial justifiquen los números.
