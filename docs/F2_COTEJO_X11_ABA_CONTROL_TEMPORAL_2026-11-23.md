# F2-R5 — Control temporal A/B/A de TUIKA por X11 (23/11/2026)

**F2 ABIERTA.** Este relevo produjo un comparador nuevo, pero NO capturas nuevas del juego. Separar A = ISO original auténtica y análisis binario, B = pruebas sintéticas/CI, C = emulación PPSSPP realmente ejecutada.

## A. Auditoría auténtica de origen, sin modificar el juego

Se leyeron las ISOs privadas ya extraídas. USA original: 305.496.064 bytes, SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. Sonda: igual tamaño, SHA256 b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa. Solo existen tres bytes diferentes tras cotejo integral: 114744872 (249→255), 114744873 (251→0), 114744874 (249→255).

Además se recodificó temporalmente en RAM (solo lectura de ISO, sin reescribirla) el atlas TUIKA 256×256 A4/IMY mediante flags y unswizzle PSP, obteniendo SHA descomprimido 3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5, SHA índices lineales a3da2c0d728288c2842b0d9164f4dd220c4713eaa19b3559ef7105f837f8106d y máscara CLUT2 382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba. Cuentas índice0=45784, índice1=10608, índice2=9144; 3506 texeles index2 en subregiones protegidas. Esto NO acredita uso durante combate.

El informe privado de metadatos F2_ABA_PREPARACION_Y_ISO_PRIVADA_20261123.json tiene SHA256 d9449c1789cfe07545ceac281e49900167fa4f77f87ec040a3a786ec1f9befa4. NO contiene bytes de la ISO ni imágenes.

## B. Nueva protección frente a falsos positivos temporales X11

Se implementó tools/f2_cotejar_x11_aba.py y tests/test_f2_cotejar_x11_aba.py. Requiere **TRES** manifiestos X11 del capturador existente tools/f2_x11_ppsspp_procfs_capture.py, en tres carpetas privadas de sesiones distintas, con tres PIDs distintos declarados. Orden: USA original antes → sonda → USA original después. Verifica ambas ISOs por tamaño/SHA exactos en disco; manifiestos X11 960×544, testigos PID/starttime/FD declarados y PNG por bytes/SHA/dimensiones sin ninguna ruta comercial dentro del repositorio. No reescala y admite ROI opcional.

La lógica en cada píxel es:
- Si USA_antes difiere de USA_después, marca píxel inestable y LO EXCLUYE de candidatos de la sonda.
- Si USA_antes es igual a USA_después, diferencia solamente en la sonda pasa a candidato cromático. Cuenta magenta NUEVO y magenta NATIVO por separado.
- Calcula ROI, bbox y fracción de control estable sin almacenar ni incrustar una máscara del juego en JSON público.
- Un candidato A1=A2 distinto de B aún puede deberse a otra animación; no es prueba causal de TUIKA ni de framebuffer PSP, MIPS, RAM, GE, VRAM o sincronización de escenas.

Las banderas de carga de ISO en juego, misma escena/fotograma, combate, procedencia GE y causalidad permanecen FALSE en el informe, aunque existan candidatos. En SYSTEM PRiSM el magenta nativo del control histórico es negativo: USA y sonda eran idénticas con 1152 píxeles magenta naturales. El nuevo comparador no inventa capturas.

**16 pruebas sintéticas locales PASS**, verificaron cambio magenta aislado, nativo ya existente, animación del control USA, validación de tres manifiestos y tres PIDs, hash de ISO/PNG adulterado, ROI, no sobrescritura y rechazo de rutas dentro de Git. Las pruebas CI del HEAD definitivo se comprueban aparte; ninguna certifica PPSSPP.

## C. PPSSPP oficial: bloqueado en este relevo

No se encontró AppImage PPSSPP 1.20.4 en el contenedor. Curl devolvió error DNS github.com y la descarga alternativa también falló. NO hay nuevos fotogramas de juego, dumps GE, PC MIPS ni pruebas de los 19 glifos. Conservar C histórico sin atribuirlo al relevo presente.

Cuando se disponga del PPSSPP oficial SHA256 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21, arrancar TRES sesiones independientes en escena de habilidad/combate realmente confirmada, con PID/socket WS/FD ISO autenticados, X11 real 960×544 y registros GE --ge-dump --ge-only del mismo estado visual. Capturar cada sesión en directorio privado diferente y ejecutar:

    python tools/f2_cotejar_x11_aba.py --manifest-usa-antes /PRIVATE/A1/witness.json --manifest-sonda /PRIVATE/B/witness.json --manifest-usa-despues /PRIVATE/A2/witness.json --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/SONDA.iso --escena COMBATE_TUIKA_CONFIRMAR --reporte-privado /PRIVATE/ABA_INFORME_NUEVO.json

Una comparación X11 A/B/A no reemplaza la prueba causal textura TUIKA_MES.IMY→RAM→MIPS→GE→VRAM ni el QA 19 caracteres áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō multicontesto. Mantener white_new_ink=False y protegidas 14 bandas/7 subregiones. No repintar CLUT2 global como traducción final: 9144 texeles quedarían recoloreados, incluidos 3506 de áreas protegidas.

## Continuidad F3/F4/F5/F6 y privacidad

Preservar avance F3 paralelo del HEAD 0c4a606c397d00e176bed4b11f62833d44803e0d: en SCRIPT.DAT las 1439 coincidencias u32 de opcode 0x02 proceden del valor repetido 8192 y NO son saltos probados. EBOOT PSP cifrado, BOOT todos ceros, sin intérprete MIPS desensamblado. Los 85 textos demo1001 de longitud distinta y 4524 scripts SCRIPT.DAT siguen BLOQUEADOS bajo --event-safe-only. ANIME000 conserva 95 cabeceras tipo02 no decodificadas y el prólogo visual en inglés sin procedencia demostrada. F5 y F6 requieren pruebas genuinas del juego/EXE/ BPS; no declarar fases completas.

Conservar corpus 9237 filas, 9235 español/2 excepciones, 2721 glifos previos, 349 PSPFS. Ningún archivo comercial ISO/BPS/FONT/EBOOT/IMY/PNG/GE/VRAM al repositorio. PR #7 permanece OPEN/DRAFT, no fusionar ni force push.

Cada relevo debe reemplazar íntegramente prompts/SIGUIENTE_TAREA.md por uno NUEVO autónomo y mostrarlo entero al usuario.
