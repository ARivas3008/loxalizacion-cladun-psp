# F3 — PPSSPP real: prueba A/B/A del nombre ANIME000.IDT y origen AÚN DESCONOCIDO del texto del prólogo (23/11/2026)

**F3 SIGUE ABIERTA. F2 SIGUE ABIERTA.** Se ejecutó PPSSPP **oficial 1.20.4** de verdad contra la ISO USA aportada por el usuario; se contrastó una copia binaria diagnóstica que difiere en **un único byte**, y se volvió al original. La prueba reveló una dependencia crítica de arranque en \`ANIME000.IDT\`, pero **NO demostró que este archivo contenga los caracteres ingleses del prólogo**. No confundir esta prueba con una traducción insertada ni con aprobación de un parche.

## Entorno autenticado, sin tocar ni distribuir binarios comerciales

- ISO USA original legítima extraída del 7z del usuario: **305.496.064 bytes**, SHA256 completo \`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f\`.
- PPSSPP original de AppImage **1.20.4 Linux x86_64**: **50.689.748 bytes**, SHA256 \`661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21\`; extraído sin cambiar el ejecutable.
- Mesa lavapipe/llvmpipe Vulkan por software en carpetas privadas, Xvfb **1280×720**, ventana SDL/X11 **960×544**. Configuración real \`GraphicsBackend = 3 (VULKAN)\`, Xvfb con GLX desactivado para evitar el fallo de contexto. Se conservó el shim externo de audio \`LD_PRELOAD\` + \`SHARUN_ALLOW_LD_PRELOAD=1\`, que solo fuerza \`SDL_AUDIODRIVER=dummy\` y NO altera código del emulador.
- Se confirmaron **capturas de pantalla auténticas** usando la ventana X11 del PPSSPP real (no imágenes generadas ni framebuffers inventados) y líneas \`Booted … Cladun_USA.iso\` del emulador. PNGs y volcados permanecen PRIVADOS; el repositorio solo almacena sus SHA.

## A/B/A y conclusión binaria exacta

**A. USA original:** arranque → título con \`Start / Continue / Options\` → selección \`Real / Retro\` → **prólogo inglés** sobre fondo animado. Captura X11 del prólogo SHA256:
\`8dbd15865eb008d2036d59e7e3bab3d130c3dfd438732c1f455dc456b22812ab\`.

**B. Sonda privada de dependencia:** se copió la ISO original y se alteró SOLAMENTE una letra del descriptor PSPFS del recurso 234 \`ANIME000.IDT\`: ASCII \`I\`=0x49 → ASCII \`X\`=0x58, resultando nombre \`ANIME000.XDT\`. **Offset absoluto de ISO 113.778.009.** Longitud del nombre, tabla y payload del archivo ANIME000.IDT conservados. Diferencias en toda la ISO **exactamente una posición** (verificado también con un auditor streaming independiente); nuevo SHA256 privado \`576e9699395dd142b666ed3b9d121db5037c63302dc0c4eee862a04ccfcdbb36\`. El emulador registra \`Booted\`, pero muestra un cuadro azul **Game crashed / Invalid Memory Access**, PC PSP \`0x08809498\`, acceso \`0x00000015\`, en \`user_main\`, **antes del menú**. Pantalla real SHA256:
\`87f9c2b4d451b41a4dc890daf031cb60cdd44d9a09ec9f8094f6244c8c78cd89\`.

**A, control posterior:** se cerró la instancia de sonda y se lanzó de nuevo la ISO USA auténtica, sin modificarse; el juego volvió a mostrar el menú correctamente. Screenshot real de recuperación SHA:
\`893c975382aa89437d7e9b7691eab9cdc9c525d0a490ae1f6e884c6499a57ba5\`.

**Alcance de la inferencia:** la diferencia de UNA letra en el descriptor PSPFS desencadena un fallo de arranque. El programa depende de ese nombre/referencia o de las condiciones de carga asociadas. **NO** es prueba de qué IMY o comando específico dibuja el texto del prólogo, porque la sonda falla **ANTES** de alcanzarlo. Es una sonda INTENCIONALMENTE NO JUGABLE, PROHIBIDA para distribución y traducción. No reproducir eliminaciones/cambios de nombre a ciegas.

## Inventario ANIME candidato; resultado de búsqueda textual negativa

Del archivo DATA.DAT original (349 PSPFS):

| PSPFS | Nombre | Bytes originales | Cabeceras literalmente \`IMY\0\` encontradas |
|---:|---|---:|---:|
| 234 | ANIME000.IDT | 3.537.936 | 231 |
| 235 | ANIME001.LDT | 287.472 | 24 |
| 236 | ANIME002.LDT | 2.067.856 | 0 |

**Solo son ocurrencias de cabecera**, no se ha demostrado su geometría, contenido dibujado, texto, paleta efectiva o uso de GPU. Las estructuras IMY de ANIME difieren de los atlas SYSGRA y la mayoría NO las acepta el decodificador F2 actual; no reinterpretar bytes de formatos 0x00/0x02 como si fueran raster F2 0xA4.

Se buscaron cadenas exactas observadas en el prólogo dentro de los 349 recursos PSPFS originales descomprimidos sin hallar la frase completa como ASCII. Una coincidencia parcial con \`some say\` apareció en \`DATABASE.DAT/MONSTER.DAT\`, concretamente en una descripción de monstruo: **es una coincidencia irrelevante**, no el prólogo. Tampoco el nombre de un recurso demuestra contenido o reproducción. Se necesitan sondas de color/imagen QUE NO IMPIDAN EL ARRANQUE o trace PSP I/O→descompresión→RAM→GE→VRAM mientras la escena REAL aparece.

## F3 narrativa y otros pendientes conservados

La auditoría F3 anterior ya había identificado 97 textos fuente de \`demo1001_00.dsf\` y \`demo1001_01.dsf\` con español en el borrador: **85** cambian longitud de instrucciones y permanecen **bloqueados por \`--event-safe-only\`**; 11 son solo candidatos de longitud igual, 1 idéntico. La prueba de este relevo mostró el **prólogo ANTERIOR** a esos diálogos, por lo que F3 tiene **dos fuentes/problemas diferentes**, no un solo conjunto de 85. F2 mantiene pendientes TUIKA en combate/habilidades, 19 glifos multicontexto y GE/VRAM; no deshacer los avances recientes de PPSSPP WebSocket/Controles.

Las **9.237** entradas del corpus, 4.524 scripts de distinta longitud aplazados, 51.705 comandos y 1.625 índices de script siguen protegidos. Ninguna ISO BPS o recurso gráfico fue versionado o distribuido y no se modificó el integrador. \`white_new_ink=False\` y \`--event-safe-only\` siguen vigentes; PR #7 abierto y DRAFT, sin merge.

## Herramienta y tests

Nueva \`tools/f3_sonda_anime000_auditar.py\` verifica contra ambos ficheros PRIVADOS tamaño y SHA completos, los 12 bytes de ambos nombres PSPFS, PSPFS_V1, y **exactamente una diferencia** en offset 113778009. No crea sondas, no edita recursos, no extrae imágenes y falla si hay otro cambio. Informe JSON nuevo fuera del repositorio:

\`\`\`bash
python tools/f3_sonda_anime000_auditar.py \
 --iso-original /PRIVATE/Cladun_USA.iso \
 --iso-sonda-privada /PRIVATE/Cladun_USA_DIAG_ANIME000_NAME.iso \
 --reporte-privado /PRIVATE/F3_AUDITORIA_UN_BYTE_NUEVA.json
\`\`\`

Se ejecutaron **14 tests sintéticos locales** sobre la herramienta y la suite completa del snapshot público disponible, **517 tests Python OK, uno omitido**; QA de corpus/borrador y \`go test ./...\` OK. Los tests no equivalen a gameplay. Documentación e informe público contienen **solo metadatos y hashes**; fotos reales privadas para el usuario.

**Siguiente F3:** mantener PPSSPP Vulkan funcional, y experimentar con una sonda aislada NO destructiva de contenido/paleta de ANIME o con captura en vivo I/O y GE durante el prólogo, para vincular concretamente una textura/rutina a sus letras. En paralelo investigar los saltos/punteros de 85 instrucciones SCRIPT.DAT en \`demo1001\`; nunca desactivar \`--event-safe-only\` por conveniencia. Ver prompt recursivo \`prompts/SIGUIENTE_TAREA.md\`.
