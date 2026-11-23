# F3-R3 — coincidencias numéricas en los eventos, NO reubicación autorizada (23/11/2026)

**F3 y F2 siguen ABIERTAS.** Este resultado procede de la ISO USA auténtica original, con SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. No se ejecutó PPSSPP en este relevo ni se alteró un byte comercial. El hallazgo es estático y no debe presentarse como semántica MIPS comprobada.

## Qué se ejecutó, y qué significa

Se extrajo en memoria `PSP_GAME/USRDIR/DATA.DAT` → PSPFS índice 231 `SCRIPT.SDT` → DSARC `SCRIPT.DAT` y `SCRIPT.TBL`, con hashes canónicos exactos. Se verificaron **1.625 bloques, 51.705 comandos y 46.308 comandos no textuales**; los siete bloques `demo1001_00/01` sumaron **878 comandos**.

Se analizaron ventanas u32 de cuatro bytes (incluso posiciones no alineadas) en argumentos de instrucciones **no textuales**, comparándolas con offsets absolutos de comandos, offsets relativos a su bloque, inicios de scripts e identificadores. Valores cero se excluyeron. El contador registra coincidencias, no destinos MIPS. Un mismo valor puede pertenecer a varias categorías y las cifras NO equivalen a cantidad de saltos.

| Coincidencia | 51.705 comandos | Siete bloques demo1001 |
| --- | ---: | ---: |
| Identificadores de script | 4.680 | 25 |
| Inicio de script | 39 | 1 |
| Offset absoluto de comando | 2.883 | 40 |
| Subconjunto anterior: offset de otro bloque | 2.706 | 40 |
| Offset relativo de comando | 1.451 | 21 |

Por ejemplo, la coincidencia de u32 con el inicio de un comando NO revela si ese campo realmente representa un puntero, un valor, un bitfield o casualidad. El análisis de 85 textos con tamaño cambiante **NO está aprobado**. La mayor concentración simple de coincidencias absolutas corresponde a opcode `0x02`, byte 5 del payload, 1.439 casos; es una prioridad de inspección, **NO una identificación de opcode de salto**.

## Código y reproducibilidad

- Auditor público: `tools/f3_referencias_riesgo.py`, solo lectura, verifica SHA/tamaño exactos de ISO y SCRIPT.DAT/TBL, analiza todos los comandos y genera metadatos únicamente. Reutiliza los parsers canónicos `tools/extract_cladun.py` y `tools/script_event_guard.py`.
- Pruebas públicas: `tests/test_f3_referencias_riesgo.py`, 11 casos sintéticos de candidatos, exclusión cero, interbloques, ventanas no alineadas, informes privados y rechazos. En el análisis local independiente del original se ejecutaron **11/11 PASS** después de corregir un supuesto incorrecto del test sobre coincidencias entre bloques.
- Resultado agregado: `reports/RESULTADO_F3_REFERENCIAS_RIESGO_2026-11-23.json`. El auditor local completo produjo un informe privado con SHA256 `67ebde958b044b3ae78d43da66686aafc4682baaab368d689592e850b2e10dd3`, sin texto original ni sprites.
- La variante pública se validará además con CI de GitHub; esa CI no contiene ISO ni emulador.

Comandos con checkout y copia ISO privada autenticada:

```bash
python tools/f3_referencias_riesgo.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/f3_candidatos_unico.json
python -m unittest discover -s tests -p 'test_f3_referencias_riesgo.py' -v
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
(cd patcher && go test ./...)
```

## Restricciones y siguiente experimento

No modificar `SCRIPT.DAT`, `SCRIPT.TBL`, texto del borrador ni `--event-safe-only` por coincidencias numéricas. Siguiente paso: clasificar por opcode y contexto los candidatos `0x02`, `0x01`, `0x07` y las instrucciones de los cuatro IDs con textos cambiantes; encontrar en PPSSPP la rutina intérprete MIPS y demostrar los destinos efectivos. Los 85 demo1001 y 4.524 scripts globales siguen bloqueados.

Separadamente F3-prólogo tiene letras inglesas de origen aún desconocido: la prueba ANIME000.XDT causó crash pre-título y **no identifica las letras**; el catálogo IMY 0x02 y sus intervalos tampoco. Trazar en PPSSPP real I/O→RAM→GE→VRAM con prólogo visible antes de cualquier sonda cromática no destructiva. Preservar toda la evidencia F2 GE-only y el ensayo TUIKA; PR #7 sigue DRAFT sin merge.
