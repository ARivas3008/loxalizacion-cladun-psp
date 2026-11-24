# R16 — localización segmentada de cuerpos SCRIPT.DAT (23/11/2026)

A: ISO USA SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, SCRIPT.DAT SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, SCRIPT.TBL SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. Reparseo independiente real: 51.705 comandos y 46.308 no textuales. Sin modificar originales.

Cuatro ventanas R15 de 32 B alcanzan el relleno posterior al último comando: offsets 7420, 218095, 223602, 227968. La ventana de 223602 cruza el slot (solo quedan 30 B). La huella continua puede ser inútil si el motor carga únicamente cuerpos de comando. Esto no prueba que realmente exista carga segmentada.

| Bloque | Inicio en archivo | Cuerpo sin relleno | Slot |
|---:|---:|---:|---:|
| 20 | 7104 | 340 | 352 |
| 757 | 218080 | 34 | 48 |
| 758 | 218128 | 5269 | 5280 |
| 759 | 223408 | 221 | 224 |
| 760 | 223632 | 4355 | 4368 |
| 761 | 228000 | 238 | 240 |
| 762 | 228240 | 332 | 336 |
| 763 | 228576 | 415 | 416 |

Cada cuerpo posee dos huellas disjuntas de 16 B (inicio y final), cada una única en SCRIPT.DAT completo, incluyendo búsquedas solapadas. El localizador read-only R16 identifica cada bloque por separado, verifica todos los bytes del cuerpo dos veces, conserva copias múltiples como candidatos y rechaza falsos positivos. No prueba ejecución MIPS; tampoco encuentra cuerpos transformados o cargados parcialmente necesariamente. Informe privado de metadatos SHA256 `f6105a09bb2bec1e58518c594bc3a6db2f9a85c18d2013394f77196513201939`.

B: 14 pruebas sintéticas nuevas PASS; 101 pruebas PASS del conjunto local parcial (no suite completa). Se colocaron los ocho cuerpos auténticos en memoria artificial, en orden inverso y separados por datos ajenos; 8/8 encontrados. **No es RAM real ni gameplay.** El núcleo recipes/scan se ejecutó sobre extracción independiente auténtica; el CLI público completo con los parsers del repositorio aún requiere checkout completo. 

C: NO EJECUTADO. curl devolvió error 6 de DNS; no se encuentra el AppImage oficial ni PPSSPP instalado. Para desbloquear, aportar el AppImage oficial Linux x86_64 de 50.689.748 B SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21` mediante archivo adjunto privado, o ejecutar pruebas en Linux propio. No subir el binario al repositorio. No repetir auditorías sin nueva información.

```bash
python -m unittest discover -s tests -p 'test_f4_r16_bloques_ram.py' -v
python tools/f4_r16_bloques_ram.py --modo preparar --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/R17_BLOQUES_NUEVO.json
# Solo con PPSSPP autentificado y rango comprobado:
python tools/f4_r16_bloques_ram.py --modo escanear --iso-original /PRIVADO/Cladun_USA_original.iso --appimage /PRIVADO/PPSSPP-v1.20.4-anylinux-x86_64.AppImage --pid PID_REAL --port 24192 --ram-start INICIO_HEX --ram-end FIN_HEX --reporte-privado /PRIVADO/R17_RAM_BLOQUES_NUEVO.json
```

Q056 NOT_RUN, 56 casos definidos. No autorizar relocalización de 4.524 textos; conservar --event-safe-only y white_new_ink=False. PR #7 DRAFT.
