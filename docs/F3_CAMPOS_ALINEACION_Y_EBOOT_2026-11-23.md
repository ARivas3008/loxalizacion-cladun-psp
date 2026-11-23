# F3-R4 — auditoría de campos de SCRIPT y cabecera EBOOT (23/11/2026)

**F3 sigue ABIERTA. F2 y F4–F6 siguen sin cerrar.** El análisis fue exclusivamente estático sobre la ISO USA ORIGINAL autenticada; no se ejecutó una nueva sesión de PPSSPP 1.20.4, pues el AppImage no estaba disponible en el entorno y la terminal no resolvía github.com. No se alteraron opcodes, diálogos, ISO, fuentes ni gráficos.

## Hallazgo causal: 1.439 ventanas numéricas corresponden a UN valor

La herramienta F3-R3 escaneaba todas las ventanas u32 de cuatro bytes en argumentos no textuales, incluso las que empiezan dentro de un campo y terminan en otro. Para el opcode 0x02 registró **1.439** coincidencias en la posición +5 con inicios absolutos de comandos.

En los **2.039** comandos de tipo 0x02 de la ISO original, el argumento siempre tiene **18 bytes**. Su disposición es estructuralmente compatible con la hipótesis **u16 + cuatro u32 little-endian** en posiciones **+2, +6, +10 y +14**, sin que se conozca todavía la función de los campos. Se comprobó la igualdad **u32(+5) = u32(+6) × 256 en los 2.039 casos**. De las 1.439 coincidencias anteriores, TODAS proceden del valor **8192 (0x2000)** repetido. NO son 1.439 destinos ni 1.439 saltos demostrados.

Los campos hipotéticos +2 y +6 registraron **cero** coincidencias con comienzos absolutos de comandos. El campo +14 registra 459, pero **442 son repeticiones del mismo valor**. Ni estos ni otros recuentos permiten asignar semántica de puntero.

## Segundo filtro: seis opcodes, no cobertura global

Nueva herramienta pública: **tools/f3_campos_alineacion.py**. Reutiliza el extractor y parser públicos de SCRIPT, exige tamaño y SHA exactos de ISO USA, SCRIPT.DAT y SCRIPT.TBL, y valida **1.625 scripts / 51.705 comandos / 46.308 instrucciones no textuales**, incluidos los siete bloques demo1001 y sus 878 instrucciones.

Solo inspecciona **0x01, 0x02, 0x07, 0x0A, 0xFB, 0xFC**, en offsets u32 seleccionados como **hipótesis**. Rechaza tamaños de argumentos inesperados. Los resultados numéricos fueron:

| Categoría | Total de los seis opcodes | Siete bloques demo1001 |
| --- | ---: | ---: |
| Posible coincidencia con offset absoluto | 803 | 16 |
| Subconjunto que coincide con offset de otro bloque | 729 | 16 |
| Coincidencia con offset relativo al bloque | 1.254 | 21 |
| Coincidencia con ID de script | 3.253 | 7 |
| Coincidencia con inicio de script | 15 | 1 |

**No se debe comparar 803 con 2.883 como una reducción porcentual**, porque difieren los alcances; el análisis anterior incluía todos los opcodes y ventanas, mientras este solo analiza posiciones elegidas en seis opcodes. Ninguna coincidencia está validada por MIPS ni autoriza reubicar scripts. El reporte local contiene además frecuencias de valores repetidos, valores numéricos distintos por campo y los casos demo1001, sin publicar payloads.

## Ejecución PSP: límite demostrado mediante ISO9660 real

Además se leyeron los dos archivos originales PSP_GAME/SYSDIR de la ISO autenticada:

| Archivo | Tamaño | SHA-256 | Resultado |
| --- | ---: | --- | --- |
| BOOT.BIN | 2.158.521 B | d2240653adc6119df174c4a3cb8451381934f6898ef2bff8d6ffe00763aebdf2 | Todos los bytes cero |
| EBOOT.BIN | 2.158.864 B | 06e39573dfc9ed18122d9b0c6c69546265b1e3f0e5806b8eb9603fcc09f2ab57 | Cabecera ~PSP, no cabecera ELF de texto plano |

Por ello no es posible desensamblar directamente estos dos archivos ISO como si contuvieran un ELF MIPS descifrado. **No excluye que PPSSPP proporcione código descifrado en memoria durante una sesión genuina; en este relevo no se obtuvo ese código ni se analizó el intérprete MIPS.**

## Pruebas y estado de integración

**A — ISO auténtica:** se verificó tamaño 305.496.064 B, SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f, recursos SCRIPT.DAT y SCRIPT.TBL y ejecutables BOOT/EBOOT. Auditoría privada solo de métricas SHA256 **9706da0fed03ce943c22d0f99ebfd2cb8ae433d09c12e3418f28a3b0a5c339b0**, sin bytes del juego.

**B — sintéticos:** **15/15 PASS locales**, con adaptadores locales privados para las interfaces de parsers que no podían clonarse por DNS; los tests publicados son tests sintéticos. La suite completa del repositorio debe validarse aparte mediante GitHub Actions y sus imports públicos reales.

**C — PPSSPP genuino:** **no se ejecutó**; no hay nuevas capturas, PCs MIPS, trazas WebSocket, GE, RAM ni VRAM.

**No se insertaron los 85 diálogos demo1001 de distinta longitud ni los 4.524 cambios SCRIPT.DAT globales.** Se conservan --event-safe-only y white_new_ink=False, 9.237 textos, 349 PSPFS y el estado F2, incluida la comparación X11 A/B aún pendiente en combate.

Para reproducir con checkout real e ISO del usuario FUERA del repositorio:

~~~bash
sha256sum /PRIVADO/USA.iso
python tools/f3_campos_alineacion.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/F3_R4_NUEVO.json
python -m unittest discover -s tests -p 'test_f3_campos_alineacion.py' -v
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
(cd patcher && go test ./...)
~~~

**Siguiente acción F3:** con PPSSPP oficial y sesión autenticada, obtener traza de intérprete MIPS real y observar llamadas/referencias efectivas sobre demo1001 antes de permitir relocalizaciones. En paralelo localizar letras del prólogo mediante I/O→RAM→GE→VRAM auténtica, no por nombres ANIME. No subir ISO, BPS, EBOOT, recursos, dumps o capturas comerciales a GitHub.
