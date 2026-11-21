# F1 — Auditoría ejecutada 21/11/2026; QA visual pendiente

## Verificado en esta sesión

- Archivo privado 7z extraído con libarchive. ISO USA **305.496.064 bytes** y SHA-256 **b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f**.
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
