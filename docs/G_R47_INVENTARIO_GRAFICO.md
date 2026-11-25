# G-R47 — inventario gráfico de la ISO USA auténtica

Auditoría estática independiente: SHA-256 de la ISO y 349 PSPFS verificados, 1468 rutas terminales incluyendo PNG del nivel ISO, 426 superficies identificadas y previsualizadas. 9 PNG, 37 MPB (incluidos dos con contador de flags extendido), 23 IMY visuales SYSGRA, 6 atlas FONT, 231 IMY ANIME000, 24 IMY ANIME001, 57 GZIP ANIME002 y 39 GZIP MAPTIP. Cuatro tablas de paleta se excluyen de imágenes. Vistas de ANIME/LDT/MAPTIP en escala de grises de índices; no se han autenticado paletas externas, ni ejecutado PPSSPP.

## Nuevos objetivos de edición (14 superficies)
- ISO/PSP_GAME/ICON0.PNG — subtítulo XMB
- ISO/PSP_GAME/PIC0.PNG — subtítulo y descripción XMB
- TITLE_LOGO.MPB — subtítulo de título
- SYSGRA.ARC/TUIKA_MES.IMY — mensajes de efectos
- SYSGRA.ARC/DAMAGE.IMY — avisos de combate
- SYSGRA.ARC/WINDOW01.IMY — SKIP/MENU
- SYSGRA.ARC/SYS1.IMY — NEW!/Any y etiquetas
- SYSGRA.ARC/MAHO_ST.IMY — Walk/Run/Mana
- SYSGRA.ARC/LVSP.IMY — estadísticas
- ANIME000.IDT — IMY[1] offset 1218960, registro 1: HELP!
- ANIME000.IDT — IMY[192] offset 3417360, registro 188: prólogo inglés 256x128
- ANIME002.LDT — record 8911 texture 0: HELP!
- ANIME002.LDT — record 8919 texture 1: WIDE
- ANIME002.LDT — record 8922 texture 0: BREAK!

**Hallazgo del prólogo**: ANIME000.IDT IMY[192] (índice desde cero), offset 3417360 (decimal), registro 188, textura 256×128, contiene el bloque inglés completo de 8 líneas. Su aspecto en archivo coincide con el texto buscado; todavía falta prueba causal C. También aparecen dos bocadillos HELP! en familias independientes. No editar sprites adyacentes.

## Disposición del inventario
6 PNG SYS.DAT2 ya implementados (QA visual pendiente); 14 objetivos nuevos; 36 superficies de créditos en ANIME000 IMY[195..212] y [213..230] (dos bloques de 18, traducir funciones y preservar nombres); 2 etiquetas estadísticas por revisar; 7 atlas/fuentes por validar; 4 condicionales (TITLE.MPB, TRIAL_BG.MPB, NIS_LOGO.MPB, ANIME002 6990); 48 preservar; 309 sin texto traducible evidente en vista de índices, pendientes de paleta/escena. Suma 426. No usar estos números como porcentaje definitivo de edición gráfica.

Mantener imágenes originales y previsualizaciones fuera de Git. No se modifica ISO, traducción, perfil R46 ni prompt de romhacking. El catálogo individual y las vistas estáticas privadas se entregaron al usuario. Siguiente fase gráfica: `prompts/GRAFICOS_R48.md`.
