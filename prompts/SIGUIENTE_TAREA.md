# NUEVA TAREA AUTÓNOMA — CLADUN ES F2: atlas A1–B3, índices +19, símbolos y tildes

Actúa como ingeniero sénior PSP/PPSSPP 1.20.4, especialista en fuentes binario/IMY, codificación Shift-JIS/CP932, desensamblado PSP MIPS, punteros, índices de atlas, localización española y QA visual. **Ejecuta modificaciones y pruebas verificables**, actualiza GitHub y mantén separadas evidencias binarias, imágenes reales y gameplay.

## 1. Repositorio y lectura obligatoria

- Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
- Rama: `integracion-eventos-segura-20261120`
- PR #7 **borrador**, base `revision-manual-dialogos`: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
- Lee **antes de modificar**: `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `reports/RESULTADOS_F1_PPSSPP_REAL_2026-11-21.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `tools/charset_es.py`, `tools/font_es_narrow.py`, `tools/font_es_patch.py`, `tools/font_es_guard.py`, `tools/menu_layout_es.py`, `tools/integrar_parche_seguro.py`, `tools/generar_parche_bps.py`, `tools/medir_f1_ppsspp.py`, `tests/test_menu_layout_es.py`.
- Confirma HEAD actual, CI, archivos afectados y el PR antes de modificar. Conservar F1 sin romper.

## 2. Estado F1 congelado y hashes inmutables para regresión

**F1 Opciones cerrada en PPSSPP real 21/11/2026** (NO juego completo). Original USA y canónica española medidos con PNG reales **756 px interior / ≈764 exterior**, x342..1097, fila y106, RGB>125 y x160..1104. Variante +1 ideográfico da 772/≈780 y se rechazó. Nueva corrección exacta del 005709 añade **10 U+3000 + 7 ASCII**, sin alterar texto literario «Decimales de daño»; valor 005710 **Sí**, 005713 **No** con un ASCII final solo de presentación. 005711/12 inalterados. Se recorrieron controles, volúmenes, Real/Retro, 4 modos decimales, círculo mágico, Capturas, retorno a Opciones/título. **Se vieron iconos L/R/cuadrado/círculo/cruz/triángulo en Controles, sin probar todavía si el motor usa código de glifo o índice físico +19: el problema F2 sigue ABIERTO.**

Hash SHA-256 ISO fuente USA (305.496.064 bytes): `b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
PPSSPP 1.20.4 AppImage oficial SHA: `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.
ISO **canónica F1** SHA: `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`.
BPS **experimental F1 canónico** SHA: `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`.
Histórica mínima anterior ISO: `9b7fc809bb106953a91d6ad6e4e23363eb7fb92760659607d484f71132b5da89` (748 exterior).
Histórica rechazado +1 U+3000 ISO: `f97fa355fce8d7ab55a81fc711e944185ebdce4a320a5077695cb445acd303c8` (780 exterior).
PNG reales privados F1 en `Cladun_ES_F1_PPSSPP_real_2026-11-21_EVIDENCIAS_PRIVADAS.zip`, SHA-256 `66f23bd7aa08301f652292ca2fc81440cd004403eb613f3ef9b0a1e6f4d66c24`, 27 capturas genuinas con hashes en manifiesto; **NO subir imágenes ni ZIP a GitHub**.
Cadena original STRTBL.DAT SHA: `16d9da36c05380cbb8af7eba53cb26c7b3e21f8ef5c80fdb90fdba20621044bf`; FONT.BIN original: `1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46`.

F1 se generó desde CSV/TXT canónicos y BPS tiene roundtrip exacto: 349 PSPFS, 345 no textuales vecinos preservados, ISO9660/DSARC ajenos idénticos, 51.705 comandos, 46.308 no textuales, 1.625 scripts, 0 offsets desplazados con `--event-safe-only`, 4.524 textos de SCRIPT.DAT aplazados. **CI de código y español debe verificarse en HEAD actual.** No atribuyas a F1 la validación de todo el motor.

## 3. Tarea F2: demostrar acceso por código vs índice

1. Estudia `FONT.ARC/FONT.BIN` (2.721 glifos USA), `FONT_00.IMY`–`FONT_05.IMY` y `tools/font_es_narrow.py`. El codec actual reasigna **19 glifos españoles A1–B3 de un byte**, insertados en posición 95, desplazando +19 índices físicos posteriores (2.626 antiguos). Conserva todos los píxeles y códigos original según auditoría.
2. Localiza usos reales de los glifos en rutinas del PSP: búsqueda de código CP932 vs acceso directo al índice/offset del atlas. Puedes examinar EBOOT, secciones ejecutables y referencias internas en copia privada y documentar desplazamientos/lookup. Aportar desensamblado reproducible con offsets/firmas, NO inventar semántica MIPS.
3. Diseña pruebas negativas y positivas controladas que distingan **código** vs **índice**: instrumentar lookup o alterar temporalmente slot de prueba en entorno privado con guardas, comparar captura con original, y restablecer invariantes. **Nunca** interpretar solo «se ve el icono» como prueba del modo de lookup.
4. Revisa en PPSSPP real los iconos R/L, cuadrado, círculo, cruz y triángulo en Controles, contexto de tutoriales, HUD y diálogos. Inspecciona `¿`, `¡`, vocales con tilde, ü, ñ, símbolos «» y el ancho/margen de cada glifo, incluidas combinaciones con texto a la derecha. Medir recorte, anclaje, superposición y avance bajo mismas resoluciones. Varias capturas auténticas por estado, hashes individuales.
5. Si hallas índices fijos, elabora reparación mínima y **modelada** que mantenga invariantes de bytes por recurso y no cambie opcodes/eventos. Prohibido parchear direcciones inventadas o mover tablas sin entender referencias.
6. Regresión obligatoria F1: PPSSPP original y candidata F1 antes/después en **Opciones** 756px interior/≈764px exterior, `005710 Sí`, `005713 No`, y recorrido de menú. Si hay desviación, retrocede F2.

## 4. Compilación segura, scripts y CI

Trabaja solo con ISO USA de origen autenticada. ISO/BPS/IMG/FONT/PNG originales o alterados deben quedar en privado, nunca GitHub. Ejecuta:
```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight-nuevo.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad-nuevo.json
(cd patcher && go test ./...)
git diff --check
export ISO_ORIGINAL='/ruta/privada/Cladun_USA_original.iso'
export SALIDA='/ruta/privada/f2-experimentos'
mkdir -p "$SALIDA"
sha256sum "$ISO_ORIGINAL"
python tools/integrar_parche_seguro.py --iso "$ISO_ORIGINAL" --candidate "$SALIDA/candidata.iso" --report "$SALIDA/integracion.json" --experimental-parcial --event-safe-only
python tools/generar_parche_bps.py --original "$ISO_ORIGINAL" --candidato "$SALIDA/candidata.iso" --informe-integracion "$SALIDA/integracion.json" --salida "$SALIDA/experimental.bps" --informe-bps "$SALIDA/bps.json" --experimental --event-safe-only
sha256sum "$SALIDA/candidata.iso" "$SALIDA/experimental.bps"
```
Usar siempre salidas inexistentes. **Nunca quitar `--event-safe-only`** para lograr cobertura de scripts o permitir 4.524 traducciones sin modelo. La auditoría tiene que confirmar de nuevo 349 PSPFS, 345 ajenos, DSARC/ISO9660 y 51.705/46.308/1.625 comandos/scripts con cero desplazamientos. Roundtrip BPS exacto; no llamar a eso prueba funcional.

## 5. Otras fases NO resueltas

F3: líneas de introducción en inglés, recurso e IDs exactos; F4: modelo formal de saltos/referencias del intérprete para 4.524 traducciones aplazadas; F5: aventura, niveles, combate, enciclopedia, inventario, retratos, guardar/cargar; F6: BPS final y EXE privado Windows verificado, regresión completa. Mantener PR #7 en borrador y no declarar localización acabada por haber cerrado F1.

## 6. ENTREGA Y RELEVO RECURSIVO OBLIGATORIOS

En esta ejecución F2, registrar causas demostradas, mapas de índices y referencias, código y tests, logs Python/Go/CI, hashes ISO/BPS/PNG y capturas PPSSPP **reales** (privadas), resultados binarios distintos de visuales, fallos/bloqueos, commits, rama y PR. Si falla una comprobación, dejar F2 ABIERTA con experimento replicable y conservar F1.

**Al finalizar, actualizar obligatoriamente `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, crear/regenerar `prompts/SIGUIENTE_TAREA.md` con un NUEVO PROMPT COMPLETO y AUTÓNOMO y MOSTRARLO AL USUARIO. El nuevo prompt deberá exigir, de nuevo, crear otro prompt al finalizar. Repetir recursivamente hasta traducir, insertar y probar por completo Cladun ES.**
