# CLADUN ES — F4-R11: hallazgo de argumento ID+100 en 0x0A y 0x0B (23/11/2026)

**Prioridad crítica: corregir el ancla dinámica propuesta en R9/R10, SIN declarar la semántica PSP MIPS probada.** Análisis A realizado sobre la ISO original USA de 305.496.064 bytes, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. Fuente SCRIPT.DAT y SCRIPT.TBL originales intactos, SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358` y `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. 1.625 bloques, 51.705 comandos, 46.308 no textuales; se recorrieron todos con parser independiente y se validó tamaño de argumentos.

## Evidencia A: barrido controlado de delta u32

En lugar de asumir que el u32 del comando es un ID literal, se contó en cada opcode cuántos valores satisfacen `argumento - delta ∈ SCRIPT.TBL_IDs` con `delta` entero en [-256, 256]. El tamaño y cantidad de comandos se verificaron antes de puntuar. Esto es inferencia de **igualdad de enteros**, no ejecución, y el barrido entre cientos de deltas puede aprovechar accidentalmente la densidad de IDs.

| Opcode | Comandos | Matches directos delta 0 | Matches tras delta 100 | Excepciones delta 100 |
|---|---:|---:|---:|---|
| 0x0A | 862 | 320 | **860** | u32=0 (1), u32=1 (1) |
| 0x0B | 166 | 75 | **158** | u32=3 (8) |
| 0x0C | 102 | **86** | 66 | u32=100 (36) entre otras |

Controles comparativos: en 0x0A, delta 99 obtiene 735 y delta 101 obtiene 426 (frente a 860 en delta 100); en 0x0B, deltas 99 y 101 dan 101 cada uno (frente a 158 en 100). Para 0x0C el máximo del barrido es delta **0 con 86**, seguido del 90 con 82; **no extrapolar +100 a 0x0C**. Con delta 100, 0x0A apunta numéricamente a 278 IDs únicos y 0x0B a 139 IDs únicos.

El hecho de que 0x0A/0x0B tengan solo los valores 0/1/3 como excepciones sugiere centinelas o casos especiales, pero **aún no se conoce su semántica**. No bautizarlos como NULL, retorno, llamada, pausa ni fin de evento sin observar el intérprete real.

## Corrección del candidato de demo1001

La propuesta anterior asociaba literalmente el comando `scr01.dsf` bloque 20, orden 20, offset en SCRIPT.DAT **7420**, opcode **0x0A**, ID de instrucción 818 y u32 **100100** con el bloque **758** / ID 100100. Ese target directo es compatible con coincidencia numérica, pero **es débil frente al patrón global**. Con la transformación candidata `argumento - 100`, el valor corresponde al script **ID 100000, bloque 757, demo1001_00.dsf**. Esto es un **destino alternativo mucho más sustentado estáticamente**, no un salto confirmado. Las dos hipótesis deben ser contrastadas con una traza C desde el proceso PPSSPP oficial.

## B y protección

Nueva herramienta `tools/f4_r11_desfase_ids.py` + `tests/test_f4_r11_desfase_ids.py`: **15 tests sintéticos PASS localmente**; incluye controles negativos, ancla literal contra desplazada, rechazo de tablas/comandos invalidos, y falsa aprobación de relocalización. La función pura se ejecutó también sobre **todos los 51.705 comandos extraídos de la ISO auténtica** mediante un parser independiente privado: reprodujo 860/862 y 158/166, así como sus excepciones y los bloques 757/758. Informe privado de metadatos, SHA256 `5cf5f3e1f7b61f1bcb1ca6b41154cab091e03dde2b2ebcd69015ce0d33bad79b`. Informe público: `reports/F4_R11_DESFASE_IDS_2026-11-23.json`, sin bytes originales del juego.

Reproducir en checkout real con copia propia privada:

```bash
python -m unittest discover -s tests -p 'test_f4_r11_desfase_ids.py' -v
python tools/f4_r11_desfase_ids.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F4_R11_NUEVO.json
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # DEBE FALLAR aun
```

C: **NO EJECUTADA**, PPSSPP v1.20.4 AppImage ausente, terminal sin DNS de github.com; descarga alternativa oficial fallida. Sin PC MIPS, RAM/GE ni pantalla nueva. No se parcheó ninguna instrucción, no se escribió ISO/BPS ni se liberaron los **4.524 cambios variables diferidos**. Se incorporan Q046 y Q047 a QA como NOT_RUN, con 47 casos definidos. La frase inglesa del prólogo, los 19 glifos multicontesto y TUIKA en combate siguen sin verificación C.

**Prueba C prioritaria siguiente:** localizar la estructura cargada correspondiente al offset 7420 de SCRIPT.DAT, detectar la lectura del u32 100100 y comprobar si el salto real dirige al **ID 100000/bloque 757**, al ID 100100/bloque 758, o a otra operación. Para 0x0B comprobar el destino de u32−100 y significado de u32=3. Mantener `--event-safe-only`, `white_new_ink=False`, los 2.721 glifos originales y 19 A1–B3, PR #7 OPEN/DRAFT, sin publicar activos comerciales ni atribuir evidencia A/B a C.

