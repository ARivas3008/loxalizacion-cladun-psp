# G-R48 — 47 variantes gráficas españolas

ISO USA original autenticada antes y después, sin modificación. Se editaron 13/14 objetivos directos, preservando LVSP (LV/SP/ATK/DEF, glosario canónico); 34/36 superficies de créditos, preservando IMY 208/226 (solo nombres). Los 17 pares editados de créditos son idénticos en índices de origen y destino. Se tradujeron cargos conservando los nombres en sus regiones originales. Las seis PNG históricas siguen implementadas pero no se reconstruyeron en esta ronda.

- SYSGRA: TUIKA_MES, DAMAGE, MAHO_ST, SYS1, WINDOW01.
- ANIME000: prólogo IMY192, HELP! IMY1, cargos de créditos.
- ANIME002: HELP! 8911/0, AMPL. 8919/1, ¡RUPTURA! 8922/0 (variantes de animación).
- TITLE_LOGO.MPB: subtítulo en atlas, tabla de tiles intacta; tiles no nulos únicos.
- PNG XMB: ICON0 y PIC0, dimensiones/modo preservados.

47/47 recursos con dimensiones y píxeles fuera de ROI exactos; 47/47 roundtrips del códec individual; 47/47 deltas reproducidos byte por byte en una segunda ejecución del script portable. 155629 píxeles alterados; 43 recursos aumentan de tamaño. El ZIP privado contiene previsualizaciones, XOR de índices/píxeles, manifiesto y código reproducible; sus hashes constan en JSON. **No** contiene ISO jugable ni parche oficial. Las vistas ANIME son índices en gris: falta confirmar CLUT, estilo, legibilidad, nomenclatura de habilidades y fase de animación en PPSSPP. El verificador de manifiesto comprueba el paquete privado por hashes, no certifica ejecución.

No modificar el corpus, la rama base ni el perfil de ROMhacking R46. No subir imágenes comerciales al repositorio. R47 CI push 45679878259 y PR 45679894263 SUCCESS. R48 debe verificar CI propio. Mantener PR DRAFT.

## Pendientes
43 recursos requieren estudiar el crecimiento comprimido; validar estructura ANIME000.IDT (longitudes, metadatos y referencias), ANIME002.LDT (offsets y descriptores), SYSGRA DSARC, TITLE MPB e ISO PNG. No reinserción ciega. 309 superficies siguen pendientes de paletas/escena; 4 condicionales, 2 abreviaturas y 7 fuentes. No declarar G 100%.
