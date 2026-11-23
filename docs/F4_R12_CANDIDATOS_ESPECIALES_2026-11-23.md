# CLADUN ES — F4 R12: valores sin correspondencia tras ID+100 en los tres opcodes (23/11/2026)

**Estado: evidencia A estática auténtica y B sintética; PPSSPP C NO EJECUTADO.** El reanálisis de la ISO USA privada (305.496.064 bytes, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`) reproduce 1.625 SCRIPT, 51.705 comandos y 46.308 no textuales. SCRIPT.DAT SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, SCRIPT.TBL SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. Archivos originales idénticos al inicio y fin; no se escribió ni ISO ni BPS.

## Nuevo resultado: también 0x0C es compatible con patrón +100 excepto un único valor repetido

Se clasificó el primer u32 little-endian del payload: **(A)** valor−100 presente como ID existente de SCRIPT.TBL o **(B)** valor sin coincidencia; B se deja SIN SEMÁNTICA. No se presupone que un B sea terminador, valor nulo, puntero, opcode especial ni retorno.

| Opcode | Comandos | u32−100 corresponde a ID | Resto: valores exactos | Distribución de fuente |
|---|---:|---:|---|---|
| 0x0A | 862 | 860 | 0 ×1; 1 ×1 | Ambos en atkDefComment.dsf, bloque 1581, offsets 626762 y 626776 |
| 0x0B | 166 | 158 | 3 ×8 | mo_atk.dsf, bloques 337 y 338 |
| 0x0C | 102 | 66 | **100 ×36** | 34 bloques (31 nombres de script), principalmente demo |

SCRIPT.TBL carece de ID **0**; por ello el argumento `100` de 0x0C produce `100−100=0` y no corresponde a ID. En R11 se informaba que delta 0 coincidía con 86/102 u32 de 0x0C frente a 66/102 con delta 100; esta estadística **no significa que 0x0C emplee de forma diferente IDs literales**: las 36 excepciones del patrón +100 son **todas el mismo valor 100** y ese valor coincide accidentalmente con un ID de SCRIPT.TBL, lo que favorece la puntuación literal. La interpretación funcional continúa DESCONOCIDA.

0x0B tiene argumento quinto byte 100 en **112** comandos y 101 en **54**; entre los 112 del primer grupo, **104** tienen ID−100 existente y **8** tienen el argumento sin correspondencia 3. Todos los 54 del grupo 101 tienen ID−100 existente. La asociación no demuestra que el byte controle una llamada o una condición.

## Anclas para prueba PSP MIPS posterior

- Comando de `scr01.dsf`: origen bloque20/orden20, offset SCRIPT.DAT **7420**, instrucción ID818, opcode 0x0A, u32=100100. Si el motor aplica ID=valor−100, destino numérico sería ID100000/bloque757; si emplea valor literal, ID100100/bloque758. **Ni una de estas rutas está confirmada por ejecución**.
- 0x0A, casos no coincidentes: `atkDefComment.dsf`, bloque 1581, instrucciones orden 9 y 11, offsets SCRIPT.DAT 626762/626776 (u32=0 y 1).
- 0x0B, ocho u32=3: `mo_atk.dsf`, bloques 337 y 338, offsets 100889/100909/100929/100949 y 101060/101083/101119/101142. Quinto byte 100.
- 0x0C, 36 u32=100: 34 bloques, 31 nombres, incluye `demo1001_00.dsf` y `demo1001_01.dsf`. No cambiar a mano esos valores.

El nuevo clasificador `tools/f4_r12_candidatos_especiales.py` rechaza longitudes incorrectas, offsets de comandos duplicados, bloques fuera de rango e IDs duplicados. `tests/test_f4_r12_candidatos_especiales.py`: **17 tests sintéticos B PASS localmente**; exactamente esos archivos (mismo Git blob SHA) están publicados. Clasificador aplicado por separado al contenido auténtico de `SCRIPT.DAT` y `SCRIPT.TBL`, informe privado solo de metadatos SHA256 `c858d33ac0ef8d23186a86f95997bfaea5d608518e7195fc8aa40995b09d4a54`. Informe público `reports/F4_R12_CANDIDATOS_ESPECIALES_2026-11-23.json`. No se presume que una suite sintética equivalga a PPSSPP.

Comandos en checkout real:

```bash
python -m unittest discover -s tests -p 'test_f4_r12_candidatos_especiales.py' -v
python tools/f4_r12_candidatos_especiales.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F4_R13_NUEVO.json
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # debe fallar al no existir cierre
```

C: PPSSPP oficial v1.20.4 **NO ejecutado**. No estaba instalado y una descarga del AppImage oficial falló en este entorno; no se han obtenido nuevas capturas, PC MIPS, RAM/GE ni pruebas de combate. Se suman los casos QA Q048 (0x0C valor100) y Q049 (0x0A valores0/1): ambos **NOT_RUN**. La matriz ahora tiene **49** casos conocidos, no es universo total. Los 85 eventos variables demo1001 y 4.524 sustituciones globales diferidas siguen bloqueados por `--event-safe-only`. TUIKA, caracteres A1–B3 y prólogo aún requieren pruebas C.

**No modificar** `SCRIPT.DAT`, originales comerciales, atlas, CLUT2 global, fuentes existentes ni PR #7 base. Preservar `white_new_ink=False`; no elevar T/G/R/Q a 100% por estos hallazgos.

