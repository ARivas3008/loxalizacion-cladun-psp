# CLADUN ES — F4 R9: clasificación original de 0x0A/0x01/0x02 y prioridades de depuración (23/11/2026)

**RESULTADO:** evidencia A estática auténtica, no evidencia C. Se releyó exclusivamente la ISO USA original privada de 305.496.064 bytes, SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. No se editó ni reconstruyó ISO, BPS, recursos o guion. Sin PPSSPP oficial 1.20.4 disponible: NO hubo PC MIPS, tramas GE/VRAM ni nuevo gameplay.

## Validación de datos y nueva precisión

En DATA.DAT se verificó PSPFS 349, SCRIPT.SDT #231 y su DSARC SCRIPT.DAT (633.344 bytes, SHA256 c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358) / SCRIPT.TBL (52.016 bytes, SHA256 f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37). El parser independiente de la ISO autentica 1.625 bloques y 51.705 comandos, incluidos 46.308 no textuales y 878 comandos en 7 bloques demo1001.

| Opcode | Comandos no textuales | Forma uniforme de argumentos | Hallazgo |
|---|---:|---|---|
| 0x0A | 862 | u32 LE, 4 bytes | 320/862 valores coinciden con alguno de 1.625 IDs de script; 183 IDs destino distintos |
| 0x01 | 4.061 | u32 LE, 4 bytes | Valores pequeños, numerosos; 5 coincidencias relativas de demo1001 con 85 |
| 0x02 | 2.039 | payload de 18 bytes | Muchos campos +2/+6 repiten 23, 32 o 55, no necesariamente direcciones |

**Candidato específico para depuración posterior:** bloque origen 20, nombre scr01.dsf, script ID 69, orden 20, offset de comando 7.420 dentro de SCRIPT.DAT, opcode 0x0A, ID de instrucción 818, argumento u32 100100. En SCRIPT.TBL existe bloque 758, demo1001_00.dsf, ID 100100, inicio de bloque 218.128. Esta coincidencia **NO prueba llamada real**. Su utilidad es localizar una única pareja origen/destino plausible para observarla durante la ejecución.

## Reducción de falsos candidatos relativos

Las 21 coincidencias numéricas del relevo R8 se concentran en seis patrones (bloque/opcode/posición/valor/orden coincidente):

| Bloque | Op | Campo | Valor | Orden coincidente | Ocurrencias |
|---:|---|---:|---:|---:|---:|
| 758 | 0x02 | +6 | 32 | 4 (0x7c) | 10 |
| 760 | 0x01 | +0 | 85 | 9 (0x7a) | 5 |
| 762 | 0x02 | +2 | 23 | 1 (0x02) | 2 |
| 762 | 0x02 | +6 | 55 | 3 (0x01) | 1 |
| 763 | 0x02 | +2 | 23 | 1 (0x02) | 2 |
| 763 | 0x02 | +6 | 55 | 3 (0x01) | 1 |

En el conjunto completo de 2.039 comandos 0x02, el campo u32 +2 contiene **23 en 1.714** ocasiones y **32 en 308**; el campo +6 contiene **32 en 1.439**, **23 en 325** y **55 en 270**. Por tanto, varias coincidencias con posiciones internas de demo1001 pueden ser numéricas incidentales. Esto NO descarta referencias ocultas, ordinales ni saltos de otra clase. Se mantienen las 21 en el inventario como CANDIDATOS SIN SEMÁNTICA, no como 21 saltos.

## Implementación reproducible y límites

Se incorpora tools/f4_r9_perfil_opcodes.py con consulta de la ISO original autenticada mediante f3_referencias_riesgo.original_script_children y script_event_guard.read_commands; report_path impide escribir dentro de Git o sobrescribir un JSON. tests/test_f4_r9_perfil_opcodes.py contiene **13 pruebas sintéticas PASS localmente** (no son PPSSPP). La misma función profile se aplicó a los comandos auténticos con un parser privado independiente y pasó las anclas 862/320/183/21/6. El informe privado de solo metadatos tiene SHA256 590db156de24d894a3109369278733296d9074f59eae52aa903b828ae0dc0bc9.

Comandos para un checkout real (NO todos se ejecutaron localmente, ya que git clone falla por DNS):

    python -m unittest discover -s tests -p 'test_f4_r9_perfil_opcodes.py' -v
    python tools/f4_r9_perfil_opcodes.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F4_R9_NUEVO.json
    python tools/qa_cobertura_4_areas.py

**Prioridad dinámica:** autenticar PPSSPP 1.20.4, PID, FD ISO y WS del mismo proceso; observar realmente lectura/dispatch de comando SCRIPT.DAT offset 7420, rastrear origen/valor/PC, destino y retorno antes de concluir que opcode 0x0A llama al script 100100. Los opcodes 0x01/0x02 requieren pruebas aparte; no inferir semántica de sus valores frecuentes.

**Estado:** F2 TUIKA/19 glifos, F3 prólogo, F4 4.524 diferidas, F5 juego integral y F6 BPS/EXE continúan abiertos. 85 textos variables demo1001 bloqueados; 11 del mismo tamaño solo simulados históricamente en memoria. Mantener --event-safe-only y white_new_ink=False, 2.721 glifos originales, PR #7 OPEN/DRAFT, sin publicar archivos comerciales ni cambiar la rama base.
