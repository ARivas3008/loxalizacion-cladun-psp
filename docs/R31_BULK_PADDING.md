# R31 — Verificación masiva por paquetes, 754 textos físicos y 1.302 preimágenes

CI final R30: push 45404618454 / PR 45404627367 SUCCESS, HEAD f38d8c1ab0a7661a554ff7563962ef882cc8a7fb. Se revisó el blob canónico completo de 9.237 filas; 5.207 SCRIPT. Se filtran traducciones más cortas, originales ASCII imprimible sin % ni barra inversa, castellano exclusivamente ASCII imprimible y 19 signos A1–B3, sin espacios finales originales en la traducción. Se excluyen 146 IDs R29/R30. No se cambia ninguna palabra del borrador en los 608 nuevos: se añade 1–2 espacios ASCII finales como experimento. **No se presume equivalencia visual;** la longitud fija protege eventos, no garantiza wrapping ni anchura en pantalla.

| Relleno | Registros | Evidencia |
|---|---:|---|
| 1 espacio | 330 | A, escrito en ISO privada |
| 2 espacios | 278 | A, escrito en ISO privada |
| 3 espacios | 187 | A preimagen, B plan |
| 4 espacios | 166 | A preimagen, B plan |
| 5 espacios | 137 | A preimagen, B plan |
| 6 espacios | 114 | A preimagen, B plan |
| 7 espacios | 90 | A preimagen, B plan |
| Total | 1302 | 608 escritos; 694 por escribir |

## Auditoría original auténtica
Los 1.302 offsets se cotejaron con los comandos y bytes del SCRIPT.DAT auténtico, 333 bloques, 37.829 bytes de preimagen, FNV32 de secuencia offset/longitud/preimagen 1592949294. FNV32 del plan completo incluyendo reemplazos 1412021638 (corpus Git). Los 608 con 1–2 espacios: 16.112 bytes de payload, 886 espacios, FNV32 480022839 y SHA-256 del plan serializado (preimagen+reemplazo) f41ae5b79ae9de53cd988551ddb734529a63c33f77f165dc7379345d6d30c4eb. Se reparsaron 51.705 comandos y cotejaron todos: 46.308 no textuales exactos, SCRIPT.TBL inalterado, cero offsets desplazados. 206 bloques nuevos, 238 con los 146 previos. SCRIPT.DAT de 754 textos SHA-256 b1e858ebf642ff0e3532dadaa01b989af25d289c75c3e0585c7153dcf3e80b03. No se publicó ningún payload de juego.

## ISO física (A)
ISO privada USA aislada, 754 textos (146 exactos +608 acolchados), SHA-256 4a9ec03611bd5a30dba28c1502de77f1c5cf288ace7e96b39fad99a948bfa39f, 306.198.528 bytes. 347 recursos ajenos a FONT/SCRIPT exactos, tres hijos DSARC hermanos exactos, 8 bloques IMY decodificados (6 recompuestos), 6 atlas IMY verificados, 2.721 glifos originales conservan métricas y píxeles, 19 nuevos, 192 bytes de margen FONT. El rango original de la ISO es idéntico excepto el slot FONT y 32 bytes autorizados de metadatos. SHA original intacta. Ninguna prueba C en PPSSPP; no es una ISO acumulada F1.

## Reproducción por paquetes
```bash
python tools/r31_bulk_padding.py --pack all
python -m unittest discover -s tests -p 'test_r31*' -v
python tools/r31_bulk_padding.py --pack short --isolated-original --allow-experimental-padding --iso-original /PRIVADO/USA.iso --candidate /PRIVADO/R31_754.iso
python tools/r31_bulk_padding.py --pack long --isolated-original --allow-experimental-padding --iso-original /PRIVADO/USA.iso --candidate /PRIVADO/R31_840.iso
python tools/r31_bulk_padding.py --pack all --allow-experimental-padding --iso-original /PRIVADO/USA.iso --candidate /PRIVADO/R31_5172_EXPERIMENTAL.iso
```
El CLI nuevo usa guardas R25/R29/R30; no se ejecutó localmente con checkout completo, la prueba A se hizo con verificador independiente. R30 modo aislado ahora acepta plan_builder con valor por defecto idéntico a antes. No se libera ISO/BPS. Objetivo experimental F1+754 = 4.478/8.248 (54,29 %); F1+1.448 = 5.172 (62,71 %) solo si se construye y valida todo. Oficial permanece 3.724/8.248, 45,15 %. 
