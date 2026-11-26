# R52 correctiva — corte 25/11/2026
Base beta 7900cb0a4b13906fe792fcbe9f64f7742618828b; integración R57 e1f73f15d0f2a748bcc8d56c31b1da7494d35986, ramas divergentes. No merge.
ISO auténtica extraída localmente: 305496064 bytes, SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. 349/349 PSPFS decodificados, 70 DSARC, 1186 miembros, 195429446 bytes expandidos. FONT.BIN 2721 glifos SHA 1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46.
STRTBL original: índices 26 Magic Circle/Equip, 28 Character Creation, 29 Character Color, 30 Dungeon, 34 Save, 421 Character creation, 447 Character color, 448 Select dungeon. Avances originales Save 28, Guardar y Ahorrar 44 cada uno; Color del personaje 118; Character Creation 116. No equivalen a contenedores medidos.
## Registro
- RC01 Save/Ahorrar: alta, STRTBL índice34 offset 0xcc8; overlay opt-in con preimagen exacta, no toca corpus. Cuatro pruebas sintéticas locales del módulo QA, aún falta ejecutar constructor y PPSSPP.
- RC02 tinta amarilla: alta, FONT_00.IMY índice15; causa histórica y ayuda F2 documentadas. Opt-in pasa a fuente acumulada, guarda 100 texels, conserva 2721 originales y 44 ligaduras por construcción; no se ha reconstruido ISO acumulada ni probado runtime.
- RC03 desbordes: alta, índices26/28/29; pendiente medida del contenedor y captura A/B/C. No cambios textuales especulativos.
- RC04 dos Mazmorra: media, candidatos 30 y 448; confirmar si son las dos opciones visibles y qué acción ejecutan. No sustitución global.
- RC05 Pudding: alta, pendientes caja, control y script exactos. Reflow auxiliar solo texto plano, no se aplica a scripts.
- RC06 146 comandos/31 candidatos relativos: crítica, sin nuevas pruebas dinámicas. RC07 seis botones: alta, proteger SYSGRA/KITAJIMA, no modificar.
## Ejecución privada
python -m tools.beta_provisional --iso /PRIVADO/USA.iso --output /PRIVADO/r52-base --profile r52 --acepto-beta-experimental
python -m tools.beta_provisional --iso /PRIVADO/USA.iso --output /PRIVADO/r52-correctiva --profile r52 --acepto-beta-experimental --corrective-ui
python -m tools.qa_corrective_r52 --draft traduccion/CLADUN_BORRADOR_ES.csv
Las salidas deben ser nuevas y privadas. La opción correctiva es experimental y puede abortar si la preimagen, la tinta o la capacidad de FONT no coinciden. Conservar métricas y hashes. Sin emulador local ni acceso al CSV grande mediante conector; no afirmar nueva evidencia C. No publicar ISO, fuentes, capturas o guardados. No incrementar porcentajes por tests sintéticos.
