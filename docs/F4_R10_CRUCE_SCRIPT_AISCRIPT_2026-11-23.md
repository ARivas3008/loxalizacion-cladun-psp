# CLADUN ES — R10: cruce estático entre SCRIPT.TBL/AISCRIPT.TBL y opcodes 0x0A/0x0B/0x0C (23/11/2026)

**F4 ABIERTA.** Análisis auténtico ISO-USA (A), tests sintéticos (B); **NO se ejecutó PPSSPP oficial (C)**. El archivo comercial original sigue intacto; no hay ISO, BPS, RAM, texturas o capturas en el repositorio público.

## Origen binario exacto

ISO USA 305.496.064 bytes, SHA256 \`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f\`. PSPFS 349; recurso #231 SCRIPT.SDT original SHA256 \`1811742d7d3e88da530c1fd2b98885e8426f7af761f7c89aecc80f34ffdbe2d4\`. DSARC contiene SCRIPT.DAT (633.344 B; SHA256 \`c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358\`), SCRIPT.TBL (52.016 B; SHA256 \`f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37\`), AISCRIPT.DAT (225.488 B; SHA256 \`1e75764dcc501f182921039d5020b71b7732d3e2c44b83bb565c70d2297acb3c\`) y AISCRIPT.TBL (17.680 B; SHA256 \`a1bf18abd792494f241f40651c6d11cbff108884c73df07e9a1395566035aede\`). Se verificaron límites, alineación 16, monotonicidad y unicidad de 1.625 IDs SCRIPT y **552 IDs AISCRIPT**. Solamente seis IDs coinciden entre ambas tablas.

## Nuevo hallazgo: familia de coincidencias, no familia de llamadas probada

| Opcode | Total instrucciones no textuales | Bytes de argumento | u32(+0) igual a ID SCRIPT | IDs SCRIPT distintos | Igual a ID AISCRIPT |
|---|---:|---:|---:|---:|---:|
| 0x0A | 862 | 4 | 320 | 183 | 0 |
| 0x0B | 166 | 5 | 75 | 67 | 0 |
| 0x0C | 102 | 4 | 86 | 49 | 0 |

**Precisión nueva:** el quinto byte de los 166 comandos 0x0B vale **100 en 112 instrucciones** y **101 en 54**; NO se conoce aún su papel. Los 320/75/86 cruces con SCRIPT.TBL son **igualdades de u32**, no 481 llamadas ni 481 saltos. Tampoco autorizan a reubicar posiciones ni prueban ausencia de referencias externas.

El candidato específico sigue siendo \`scr01.dsf\`, bloque 20 / orden 20, comando \`SCRIPT.DAT\` offset decimal 7420, opcode 0x0A / ID de instrucción 818 / u32 100100, que coincide con el ID del bloque 758 \`demo1001_00.dsf\`. **No hay traza PSP MIPS de esa lectura ni transferencia demostrada.**

## Comprobaciones y reproducibilidad

Se añadió \`tools/f4_r10_cruce_script_ai.py\` con lector autenticado de los cuatro hijos DSARC, cruce exclusivo de argumentos +0 y rechazo de tablas erróneas, offsets inválidos o longitudes alteradas. \`tests/test_f4_r10_cruce_script_ai.py\`: **15 tests sintéticos PASS local**, incluyendo colisiones de ID, datos malformados, quinto byte 0x0B y bloqueo de reubicación. La función de análisis se aplicó a la ISO original mediante parser independiente; informe privado de metadatos SHA256 \`385bf2a9471287adebf226a921a4fbf8dd17b7017385ec1da12fb39d577ee7ea\`. Los contadores se publican en \`reports/F4_R10_CRUCE_SCRIPT_AISCRIPT_2026-11-23.json\`, sin comandos ni texto fuente comercial.

En checkout y con copia privada de la ISO original:

\`\`\`bash
python -m unittest discover -s tests -p 'test_f4_r10_cruce_script_ai.py' -v
python tools/f4_r10_cruce_script_ai.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F4_R10_NUEVO.json
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # debe fallar con 4 áreas abiertas
\`\`\`

En este entorno PPSSPP oficial 1.20.4 no estaba instalado y la descarga oficial del AppImage en GitHub falló; el terminal tampoco resolvió github.com. Los tests B y auditorías A **no** son evidencia C. Se añadieron Q044 (0x0B y quinto byte) y Q045 (0x0C y namespaces) como **NOT_RUN**; matriz ahora 45 casos definidos, universo incompleto.

## Siguiente prueba imprescindible

PPSSPP oficial autenticado 1.20.4: ISO real, PID/starttime, fd ISO, socket WebSocket mismo proceso. En escena que ejecute \`scr01.dsf\`, observar consumo exacto de 0x0A en offset 7420 y su retorno; instrumentar 0x0B (byte 100/101) y 0x0C como controles comparativos. Registrar PC MIPS auténtico, registro/puntero RAM real e IDs consumidos; si no hay causalidad, descartar hipótesis. No insertar 85 textos variables demo1001 ni los 4.524 pospuestos antes de demostrar semántica completa. Conservar F2 TUIKA, 19 glifos, F3 prólogo, F5 pruebas de juego y F6 BPS/EXE como pendientes; \`--event-safe-only\`, \`white_new_ink=False\`, PR #7 DRAFT sin merge.

