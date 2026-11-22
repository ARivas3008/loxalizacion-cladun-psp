# F1 — Auditoría ejecutada 21/11/2026; QA visual pendiente

## Verificado en esta sesión

- Archivo privado 7z extraído con libarchive. ISO USA **305.496.064 bytes** y SHA-256 **b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f**.
- ISO9660 original: `DATA.DAT` offset **113.770.496** bytes, tamaño **191.697.408**, cabecera `PSPFS_V1` y **349 entradas** con nombres únicos y rangos válidos. Esto audita el *original*, no una ISO recompilada.
- PR #7 abierto como borrador sobre `revision-manual-dialogos`, rama `integracion-eventos-segura-20261120`.
- Se añadieron `tools/experimento_onoff_f1.py` y `tests/test_experimento_onoff_f1.py`. Su sintaxis se comprobó mediante `python -m py_compile`; no se contó esa prueba como suite Python completa.
- El generador nuevo no modifica fuentes canónicas: copia 9.237 registros, exige preimagen exacta de 005710/005713, preserva 005711/005712, aplica expresamente el override 005709 a CSV alternativos y comprueba el códec reversible. Propuesta **no aprobada**: `005710: "          EN" → "          Sí"`, `005713: "         APAGADO" → "         No"`. Incluye segunda opción `activado-desactivado`.
- La sangría ASCII inicial se conserva literalmente; **el anclaje visual derecho no está demostrado**. El modo `--iso` permite medir avances de glifos originales.

## Bloqueos y distinción de evidencia

- No hay PPSSPP instalado; la descarga oficial del AppImage v1.20.4 desde GitHub falló por ausencia de red/DNS. El AppImage oficial publicado tiene SHA-256 **661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21**. No se ejecutó PPSSPP real ni se obtuvieron capturas nuevas.
- La evidencia visual anterior del **20/11** permanece histórica: original 756/≈764 px, v0.1.5 324/≈332 px, solo 005697 324/≈332 px, solo 005709 740/≈748 px, cinco espaciados 740/≈748 px. Método: fila y=106; RGB>125; x=160..1104. Los **16 px residuales** siguen sin verificación.
- Candidata previa +1 U+3000: ISO **f97fa355fce8d7ab55a81fc711e944185ebdce4a320a5077695cb445acd303c8**, BPS **279bd99d7a0cfb87fd1bb4a03ee67ecc250d51563e14f12e213283922a8634fc**, **SIN captura válida**.
- Basal previo F1: ISO **9b7fc809bb106953a91d6ad6e4e23363eb7fb92760659607d484f71132b5da89**, BPS **5047fa7b565f84ec204f7f1dde4e47752eb2013af8daa40d68714ca7255b1566**. No se regeneraron ISO/BPS en esta sesión: ni SHA nuevos ni roundtrip nuevo.
- No hubo checkout local completo por falta de conectividad para Git; no se ejecutaron en local la suite completa Python, Go ni la integridad de candidatas. No se inspeccionó cursor, ayudas, volumen, Real/Retro, decimales, círculos, Capturas, Controles o retorno. **F1 ABIERTA.**
- ZIP comercial privado de capturas anteriores: SHA-256 **4d7f83259dcfe37242700c6cce1dbbee9e36945c1860d5e9fff9a30c7b58cae2**; no disponible en esta sesión, no subir a GitHub.

## Ensayos reproducibles pendientes

```bash
export ISO_ORIGINAL=/ruta/privada/Cladun_USA_original.iso
mkdir -p /ruta/privada/f1-21nov
python tools/experimento_onoff_f1.py --iso "$ISO_ORIGINAL" --modo si-no --ids 005710 --salida-csv /ruta/privada/f1-21nov/on.csv --reporte /ruta/privada/f1-21nov/on.json
python tools/experimento_onoff_f1.py --iso "$ISO_ORIGINAL" --modo si-no --ids 005713 --salida-csv /ruta/privada/f1-21nov/off.csv --reporte /ruta/privada/f1-21nov/off.json
python tools/experimento_onoff_f1.py --iso "$ISO_ORIGINAL" --modo si-no --salida-csv /ruta/privada/f1-21nov/onoff.csv --reporte /ruta/privada/f1-21nov/onoff.json
python tools/integrar_parche_seguro.py --iso "$ISO_ORIGINAL" --borrador /ruta/privada/f1-21nov/onoff.csv --candidate /ruta/privada/f1-21nov/onoff.iso --report /ruta/privada/f1-21nov/onoff-integracion.json --experimental-parcial --event-safe-only
python tools/generar_parche_bps.py --original "$ISO_ORIGINAL" --candidato /ruta/privada/f1-21nov/onoff.iso --informe-integracion /ruta/privada/f1-21nov/onoff-integracion.json --salida /ruta/privada/f1-21nov/onoff.bps --informe-bps /ruta/privada/f1-21nov/onoff-bps.json --experimental --event-safe-only
```

Usar rutas de salida inexistentes. Ensayar +1 espacio en 005709 como CSV alternativo y exigir hash histórico antes de continuar. Comparar PPSSPP con original y F1, todas las posiciones del cursor, ayudas y al menos dos estados por pantalla; no dar por solucionado F2. Repetir auditoría 349 PSPFS/DSARC/ISO9660, 51.705 comandos, 46.308 no textuales, 1.625 scripts, cero desplazamientos, 4.524 traducciones pospuestas. No consolidar CSV/TXT ni cerrar F1 sin evidencia de emulador.

## Medición adicional desde FONT.BIN original (ejecución 21/11)

Se descodificó **DATABASE.DAT (IMY: 230876 bytes almacenados, 620032 expandidos)** y **FONT.ARC** de la ISO privada, sin exportar assets. Los miembros originales quedaron autenticados: `STRTBL.DAT` SHA-256 `16d9da36c05380cbb8af7eba53cb26c7b3e21f8ef5c80fdb90fdba20621044bf` (17744 B) y `FONT.BIN` SHA-256 `1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46` (10888 B; 2721 glifos).

En STRTBL hay 654 punteros y 651 cadenas no vacías. Secuencia literal de índices **501–505**: 005709 = «Show decimal points for damage» con siete U+3000; 005710 = diez ASCII + ON; 005711 = un U+3000 + «Under 1 ON»; 005712 = un ASCII + «Under 10 ON»; 005713 = nueve ASCII + OFF. Confirmar que el borrador de 005711–12 conserva su semántica antes de aprobar un cambio de ON/OFF.

| Cadena con sangría | Ancho real de avance de fuente (px) |
| --- | ---: |
| 005710 original `          ON` | 84 |
| 005710 borrador `          EN` | 84 |
| 005710 candidata `          Sí` | 80 |
| 005713 original `         OFF` | 84 |
| 005713 borrador `         APAGADO` | 115 |
| 005713 candidata `         No` | 77 |
| 005710 alternativa `          Activado` | 123 |
| 005713 alternativa `         Desactivado` | 135 |

Las métricas del glifo `í` se obtienen de su base estrecha `i`, conforme al códec A1–B3. Para 005709, presentación mínima = **303 px** de avance; +1 U+3000 = **318 px** (+15 px de avance, sin que ello pruebe +16 px de caja PPSSPP). **No adoptar «Sí/No» sin ajuste de anclaje y comparación visual.** Datos también en `reports/f1_metricas_onoff_original_2026-11-21.json`.

## CI de este commit

GitHub Actions `44904208388` y `44904203528` en el commit `caa60c00121e04d8bf955ca9ed9872cbf39cc5d1`: **SUCCESS**. Log del primero: **130 pruebas Python** en 4,486 s; comprobación de integridad y borrador, integrabilidad estática, `go test ./...` y compilación Windows x64 **sin payload** correctas. Esto no ejecuta PPSSPP ni compila ISO/BPS privados.


## Nueva auditoría binaria y experimento aislado +1 U+3000 (21/11/2026)

Una nueva auditoría independiente **realmente ejecutada** sobre la ISO USA privada, sin alterar sus bytes, confirmó SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, 305.496.064 bytes, 16 registros ISO9660 (12 archivos), `DATA.DAT` offset 113.770.496 y tamaño 191.697.408, SHA-256 `7f4db811e5d079ed58c15ee21cc14ab472d58d93f5c97378982a922c39af3404`. Recontó 349 PSPFS con 349 nombres únicos y DSARC: 30 miembros DATABASE.DAT, 7 FONT.ARC, 4 SCRIPT.SDT; 654 punteros STRTBL / 651 textos; 2.721 glifos fuente originales. En el SCRIPT.DAT original leyó y validó **1.625 inicios de script, 51.705 comandos, 46.308 no textuales y 5.397 textuales** con terminación/padding válido. Informe sin recursos comerciales: `reports/auditoria_original_f1_2026-11-21.json`. Auditor reproducible versionado: `tools/auditar_f1_fuente_original.py`. **Solo certifica el origen, NO una candidata BPS.**

Se midieron desde `FONT.BIN` original los avances de los 32 rótulos/ayudas 005687–005718, cruzándolos con las cadenas del borrador. Informe detallado sin payload: `reports/metricas_menu_f1_2026-11-21.json`. Destacan `005709`: original 303 px / borrador 111 / adaptación mínima 303 / variante +1 U+3000 318; `005710`: original ON 84 / borrador EN 84 / «Sí» sin cambios de sangría 80; `005713`: original OFF 84 / borrador APAGADO 115 / «No» 77. Son **avances tipográficos estáticos**, no anchuras visuales PPSSPP. La variación +15 px de avance sugiere comprobar la cuantización en 16 px, pero NO demuestra que el menú vuelva a 764 px.

Nuevo `tools/experimento_menu_f1_residuo.py` crea un CSV alternativo con **exactamente una fila modificada: 005709.espanol** = «Decimales de daño» + 10 U+3000 + 6 ASCII + 1 U+3000; exige 9237 registros, el origen exacto y destinos inexistentes. Su informe marca explícitamente los hashes históricos como EXPECTATIVA NO RECONSTRUIDA. `tests/test_experimento_menu_f1_residuo.py` añade cuatro pruebas de aislamiento/rechazo. Al usar `--borrador`, no se activa el override automático canónico; esta herramienta sí incorpora el relleno correcto para el ensayo.

CI del commit `3c6276dc7f13974fbd085510c96e91cff53c1f3c`: ejecuciones `44905002958` y `44904998228`, ambas SUCCESS; **134 pruebas Python** (incluidas 4 nuevas), pruebas Go, corpus/borrador, integrabilidad y compilación Windows pública sin payload aprobados. No se ejecutaron PPSSPP real, reconstrucción ISO/BPS, roundtrip BPS ni análisis de una candidata en esta sesión: faltó el AppImage (red/DNS inaccesible), los CSV canónicos no se cambiaron, F1 permanece ABIERTA. No se subieron ISO, BPS, capturas ni recursos comerciales.
