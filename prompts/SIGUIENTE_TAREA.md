# NUEVA TAREA AUTÓNOMA — Cladun ES F1: PPSSPP real, ancho y ON/OFF

Actúa como especialista PSP, ingeniería inversa, fuentes, codificación, BPS, QA funcional y PPSSPP 1.20.4. **Ejecuta cambios y pruebas reales y actualiza GitHub**. Nunca confundas auditoría binaria con prueba visual o de juego; no fabriques capturas ni declares aprobaciones sin evidencias.

## Repositorio y lecturas obligatorias

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: `integracion-eventos-segura-20261120`
PR **#7 borrador**: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base: `revision-manual-dialogos`.

Antes de modificar: `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-20.md`, `docs/EXPERIMENTO_MENU_F1_2026-11-20.md`, `docs/RESULTADO_F1_SESION_2026-11-21.md`, `reports/RESULTADOS_F1_PPSSPP_REAL_2026-11-20.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `tools/menu_layout_es.py`, `tools/integrar_parche_seguro.py`, `tools/experimento_menu_f1.py`, `tools/experimento_onoff_f1.py`, `tools/generar_parche_bps.py`, `tests/test_menu_layout_es.py` y `tests/test_experimento_onoff_f1.py`.

## Hechos reproducidos y evidencias anteriores

**21/11/2026:** el archivo 7z proporcionado se extrajo de verdad. ISO USA 305.496.064 bytes, SHA-256 **b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f**. ISO9660 original `DATA.DAT` offset **113.770.496**, tamaño **191.697.408**, cabecera `PSPFS_V1`, 349 nombres únicos y offsets/rangos válidos. Es auditoría de entrada, NO de candidata. Se introdujo generador aislado para valores 005710/005713 con corrección explícita 005709 y pruebas Python, **sin editar CSV maestro/TXT**. PPSSPP **NO se ejecutó el 21/11** por bloqueo de descarga/DNS; no hay capturas nuevas y no hay ISO/BPS nuevos verificados. Revisar resultado de CI del commit actual; no asumir éxito por los tests de sintaxis.

**20/11/2026 (histórico validado PPSSPP):** PPSSPP real 1.20.4, Xvfb 1280×720×24, ventana 960×544+160+88, software renderer, SDL_AUDIODRIVER=dummy; entrada con Return, Down, z. Anchos interior/exterior: ISO USA **756/≈764**, v0.1.5 **324/≈332**, solo 005697 **324/≈332**, solo 005709 **740/≈748**, cinco espaciados **740/≈748**. Medición de PNG auténtico sin editar, fila **y=106**, RGB>125, intervalo **x=160..1104**. Causa demostrada: 005709 perdió relleno ideográfico en `DATABASE.DAT/STRTBL.DAT`. El override canónico en `tools/menu_layout_es.py` produce «Decimales de daño» + 10×U+3000 + 6×espacio ASCII, sin cambiar textos literarios; **no se activa para `--borrador` alternativo**. Permanecen 16 px. ZIP privado histórico `Cladun_F1_capturas_reales_PPSSPP_2026-11-20.zip`, SHA-256 **4d7f83259dcfe37242700c6cce1dbbee9e36945c1860d5e9fff9a30c7b58cae2**; no subir a GitHub.

Hashes previos: ISO canónica F1 **9b7fc809bb106953a91d6ad6e4e23363eb7fb92760659607d484f71132b5da89**, BPS **5047fa7b565f84ec204f7f1dde4e47752eb2013af8daa40d68714ca7255b1566**. Variante +1 U+3000 de 005709 **sin captura útil**: ISO **f97fa355fce8d7ab55a81fc711e944185ebdce4a320a5077695cb445acd303c8**, BPS **279bd99d7a0cfb87fd1bb4a03ee67ecc250d51563e14f12e213283922a8634fc**. Original `STRTBL.DAT` **16d9da36c05380cbb8af7eba53cb26c7b3e21f8ef5c80fdb90fdba20621044bf**, `FONT.BIN` **1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46**. AppImage oficial PPSSPP https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage, SHA-256 **661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21**.

## Tareas inmediatas en orden

1. Recupera el AppImage oficial y prueba su hash; configura PPSSPP real y PNG auténticos. Repite +1 U+3000 para **005709**, exclusivamente en un CSV de borrador copiado; hash de ISO debe coincidir con `f97fa355...303c8` o detén la prueba. Mide **16 px residuales** con coordenadas/umbral anteriores. Comprueba bordes, cursor, ayudas, solapes; si falla, **conserva la solución mínima 005709** y estudia rutinas de dimensionado/redondeo.
2. IDs y valores: `005710` original «          ON», borrador «          EN» (no natural); `005713` original «         OFF», borrador «         APAGADO»; `005711–005712` deben permanecer intactos. Usa `tools/experimento_onoff_f1.py`: variantes separadas ON, OFF y ambas, modo `si-no` (Sí/No) y opcional `activado-desactivado`. **La herramienta incluye 005709 ya corregido**. Con `--iso` produce medidas estáticas de avances; **no garantiza anclaje visual**. Inspecciona capturas/cursor/márgenes ANTES de aprobar. Solo si apruebas cambio literario canónico sincroniza CSV, **ambos TXT**, bitácora antes/después y vistas derivadas en un mismo commit; deja los espacios invisibles en override de presentación.
3. Recorre **todas** las posiciones de Opciones y sus cambios: volumen efectos/música, Real/Retro, decimales de daño, efectos de círculo, Capturas, Controles, regreso al menú; al menos dos PNG auténticos por pantalla, con hashes. Comparar original/canónica/+1/ON/OFF. Examina L/R y cuadrado, círculo, cruz, triángulo. No declara F2 resuelta hasta demostrar acceso por código frente a índice de atlas desplazado +19 por 19 glifos A1–B3.
4. Reconstruye ISO/BPS **privadas** por variante con roundtrip BPS exacto; verifica **349 PSPFS**, DSARC, ISO9660 ajenos, **51.705 comandos, 46.308 no textuales, 1.625 scripts, cero offsets movidos** y **4.524 traducciones de script aplazadas**. Nunca quitar `--event-safe-only`. Archivos de salida siempre inexistentes. Mantén PR #7 en borrador mientras F1 esté abierta.

## Comandos (en checkout de rama)

```bash
git fetch origin && git switch integracion-eventos-segura-20261120 && git pull --ff-only
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f1-preflight-nuevo.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f1-integrabilidad-nuevo.json
(cd patcher && go test ./...)
git diff --check
export ISO_ORIGINAL=/ruta/privada/Cladun_USA_original.iso
sha256sum "$ISO_ORIGINAL"
mkdir -p /ruta/privada/f1-nueva
python tools/experimento_onoff_f1.py --iso "$ISO_ORIGINAL" --modo si-no --ids 005710 --salida-csv /ruta/privada/f1-nueva/on.csv --reporte /ruta/privada/f1-nueva/on.json
python tools/experimento_onoff_f1.py --iso "$ISO_ORIGINAL" --modo si-no --ids 005713 --salida-csv /ruta/privada/f1-nueva/off.csv --reporte /ruta/privada/f1-nueva/off.json
python tools/experimento_onoff_f1.py --iso "$ISO_ORIGINAL" --modo si-no --salida-csv /ruta/privada/f1-nueva/onoff.csv --reporte /ruta/privada/f1-nueva/onoff.json
python tools/integrar_parche_seguro.py --iso "$ISO_ORIGINAL" --borrador /ruta/privada/f1-nueva/onoff.csv --candidate /ruta/privada/f1-nueva/onoff.iso --report /ruta/privada/f1-nueva/onoff-integracion.json --experimental-parcial --event-safe-only
python tools/generar_parche_bps.py --original "$ISO_ORIGINAL" --candidato /ruta/privada/f1-nueva/onoff.iso --informe-integracion /ruta/privada/f1-nueva/onoff-integracion.json --salida /ruta/privada/f1-nueva/onoff.bps --informe-bps /ruta/privada/f1-nueva/onoff-bps.json --experimental --event-safe-only
sha256sum /ruta/privada/f1-nueva/onoff.iso /ruta/privada/f1-nueva/onoff.bps
```

Para +1 generar CSV separado de 9.237 filas con **solo 005709.espanol** = «Decimales de daño» + 10 U+3000 + 6 espacios ASCII + 1 U+3000; dar `--borrador` a integrador, comparar hash esperado y detenerse ante cualquier diferencia. No subir ISO, BPS, FONT, PNG ni otros recursos comerciales a GitHub.

## Cierre y relevo RECURSIVO OBLIGATORIO

Al finalizar identifica las pruebas realmente ejecutadas, SHA de binarios/PNG nuevos, logs Python/Go/CI, capturas PPSSPP reales y rutas privadas, auditoría binaria distinta de visual y funcional, fallos y bloqueos concretos. Anota commits, rama y PR. **Actualiza `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y REGENERA `prompts/SIGUIENTE_TAREA.md` con OTRO PROMPT COMPLETO y AUTÓNOMO; muéstralo al usuario. El nuevo prompt DEBE exigir, a su vez, generar otro prompt al cerrar la siguiente tarea.** Repetir hasta implementar y probar todo el juego. F2: atlas/glifos; F3: intro inglés; F4: intérprete/4.524 scripts; F5: gameplay; F6: BPS/EXE/QA final. **No avanzar si F1 sigue bloqueada sin documentarlo.**
