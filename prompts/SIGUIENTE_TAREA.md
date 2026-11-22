# CLADUN ES — SIGUIENTE RELEVO AUTÓNOMO F2: traza RAM/GE/VRAM, 19 glifos, regresión F1

Actúa como especialista sénior PSP MIPS, PPSSPP oficial 1.20.4, debugger WebSocket, comandos GE/VRAM, IMY/CLUT, DSARC/PSPFS, CP932, fuentes, BPS, español natural y QA funcional. Esta NO es una solicitud de instrucciones: debes hacer trabajo verificable, editar código y pruebas, actualizar GitHub y entregar evidencias auténticas. No inventar resultados ni declarar que se ha ejecutado una prueba si no se ejecutó. Al finalizar, REESCRIBE COMPLETAMENTE este mismo archivo prompts/SIGUIENTE_TAREA.md con OTRO prompt autónomo completo y exige de nuevo esa misma obligación recursiva, sin interrupción hasta completar F2, F3, F4, F5 y F6.

## 1. Repositorio, branch y lectura íntegra obligatoria

GitHub: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: integracion-eventos-segura-20261120
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Rama base: revision-manual-dialogos. Mantener PR en DRAFT.

Antes de tocar archivos consulta HEAD, cambios, árbol y GitHub Actions reales. Ejecuta:
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD

Lee íntegros AGENTS.md; README.md; docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md; docs/RESULTADO_F1_PPSSPP_2026-11-21.md; docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md; docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md; docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md; reports/RESULTADOS_F2_ATLAS_PPSSPP_2026-11-21.json; reports/RESULTADOS_F2_ICONOS_TINTA_PPSSPP_2026-11-21.json; reports/RESULTADO_F2_AUDITORIA_ORIGEN_2026-11-21.json; reports/ESTADO_CONTINUIDAD_PPSSPP.json; prompts/SIGUIENTE_TAREA.md. Revisa también las herramientas en tools/, tests/, patcher/ y workflows .github.

No publicar ISO, BPS, EBOOT, RAM, FONT.ARC, DATA.DAT, texturas, GPU dumps, ni capturas comerciales; todos se mantienen privados. No sobrescribir trabajo de otras sesiones ni forzar HEAD.

## 2. Estado probado y límites

ISO USA auténtica SHA-256 completo de 64 caracteres:
b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f
Tamaño: 305496064 bytes. ATENCIÓN: una versión del hash en una solicitud tenía 62 caracteres, por lo que era errónea.

ISO canónica F1 SHA:
496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986
BPS privado de USA a F1 SHA:
daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd
PPSSPP AppImage 1.20.4 SHA:
661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21

F1 Opciones ya se aprobó históricamente en PPSSPP real Xvfb 1280×720 con ventana 960×544: 756 px interiores, aproximadamente 764 exteriores. IDs 005709 (diez espacios ideográficos + siete ASCII), 005710 «Sí», 005713 «No» con un espacio final solo en presentación. NO interpretar capturas a pantalla completa de F2 como revalidación del F1 en ventana 960×544. No modificar estos valores sin repetir regresión.

F2: atlas español 2740 frente a 2721 glifos originales; 19 incorporados en códigos de un byte A1–B3. Originales preservados en códigos, raster y métricas. Se demostró búsqueda MIPS código→índice para texto en tabla RAM 0x09075000, PC 0x089089C8 instrucción lhu t2,0(t1). Esto no prueba iconos.

Controles obtiene seis iconos de DATA.DAT → SYSGRA.ARC → KITAJIMA_KARI.IMY. PSPFS 349 entradas; SYSGRA índice 225 y offset local DATA.DAT 895488; DSARC 27 miembros, KITAJIMA índice 17, offset 57856, longitud 2480, SHA 0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190. Nueva auditoría real independiente de ISO USA confirmó DATA.DAT en offset ISO 113770496; KITAJIMA en offset ISO absoluto 114723840 (0x06D68C00), 27 cambios RGB magenta aislados simulados en memoria, ningún archivo ISO escrito. Herramienta nueva tools/f2_auditar_origen_iconos.py, con siete pruebas unitarias sintéticas. Este último análisis es SOLO BINARIO: NO traza RAM/GE/VRAM ni demuestra HUD, tutoriales o combate.

La sonda magenta previa de PPSSPP real cambió seis iconos de Controles y preservó texto/bordes, con 348 PSPFS y 26 DSARC vecinos intactos. ISO diagnóstica SHA b634fe468158a7ba5c3242896d4b1c43e711de53a19869c3b469a4877bc2e73d; BPS desde F1 SHA 4b0a47d9ff2b33f364be45f508ab4510776c0bb6b4cc7245236699c5fbe25c61.

19 signos españoles: áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō. La sonda privada del ID 005694 mostró algunos trazos amarillos: FONT_00.IMY CLUT15 RGB(247,247,0) frente a CLUT1 RGB(255,255,255). tools/font_es_narrow.py permite white_new_ink=True solo OPTATIVO; 100 texels nuevos 15→1, 2721 glifos antiguos intactos. ISO diagnóstica amarilla SHA 58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca; ISO corregida privada SHA a42731988835bddb9dc81ef6d242b9c5029030256f210838881a1d48aed2de33; BPS desde diagnóstica amarilla (NO USA) SHA 2a698e1efaa1c2333dbd86ac8c3a9fabbd369382c4b8c7d3ad0ab7c7f2ffac3f. PNGs reales previos dieron 516 píxeles amarillos antes frente a 0 después en una ayuda. NO activar blanco por defecto antes de QA multicontesto y regresión F1.

El último relevo NO dispuso del AppImage oficial ni de ISO F1 privada; por eso NO aportó nuevas capturas, nuevos BPS, traza MIPS/GE/VRAM ni QA funcional. Mantener claramente separadas las evidencias históricas de las pruebas nuevas.

## 3. Primera tarea prioritaria: encontrar la traza MIPS RAM→GE→VRAM

Con PPSSPP oficial 1.20.4 e ISO F1 autenticada, comprobar SHA antes de arrancar. Usar depurador local, incluida la interfaz WebSocket ws://127.0.0.1:24192/debugger con subprotocolo debugger.ppsspp.org, si está disponible.

Detectar carga exacta de SYSGRA/KITAJIMA desde DATA.DAT: I/O de disco, dirección RAM comprimida, buffer de descompresión, dirección de textura raster, transferencias a memoria gráfica, comandos GE y PC MIPS concreto de cada operación. Capturar registros, disassembly, tamaños, bytes de comandos y referencias verificables. No confundir offset ISO 0x06D68C00 con dirección RAM. Mostrar la cadena completa y el momento de dibujado final o marcar expresamente cada tramo NO DEMOSTRADO.

Hacer modificaciones aisladas/reversibles en copias verificadas, con controles positivos y negativos; comparar F1 y magenta. Probar Controles, HUD, tutoriales, ayudas, diálogos y combate, sin suponer recursos comunes. Obtener dos capturas PNG sin retoques por pantalla y registrar sus SHA256 en un manifiesto PRIVADO. Nunca atribuir GE a un PC inventado, ni llamar prueba real a simulación de memoria.

## 4. Segunda tarea: QA de los 19 glifos

En PPSSPP real observar individualmente los 19 signos de lista anterior y sus combinaciones. Medir ancho visual, avance, márgenes, baselines, altura, clipping, separaciones, interacción con iconos L/R/□○×△, tildes superiores y mayúsculas, ñ/Ñ, ü/Ü, ¿¡, «» y ō. Comparar con texto normal blanco y entre tinta amarilla y blanca opcional.

Explorar escenas reales HUD, ayuda, tutorial, diálogos, opciones y combate; cuando falte un carácter usar exclusivamente variante PRIVADA de diagnóstico creada con tools/generar_probe_f2_glifos.py, preservando los 9237 registros y NO tocando corpus canónico. Usar tools/generar_probe_f2_tinta.py para cambio optativo. Cada pantalla validada necesita dos PNG auténticos y SHA; añadir resultados por glifo y contexto. Si se adopta tinta blanca por defecto, antes repetir PPSSPP Opciones en ventana 960×544, confirmar 756/764 px, «Sí/No», 005709 y no regresiones.

## 5. Invariantes binarios imprescindibles

Mantener 349 PSPFS; 345 recursos fuera de los cuatro contenedores de localización; 348 recursos PSPFS ajenos si solo cambia FONT.ARC o SYSGRA.ARC; 26 DSARC vecinos de KITAJIMA; ISO9660 no intervenido intacto; 51705 comandos SCRIPT.DAT, 46308 no textuales, 1625 inicios, cero desplazamientos y 4524 traducciones script aplazadas. No retirar NUNCA --event-safe-only. Integración candidata desde USA: --experimental-parcial --event-safe-only. Parche BPS experimental: --experimental --event-safe-only. BPS con origen siempre identificado USA, F1 o diagnóstico; roundtrip SHA byte exacto. Conservar las ISO origen y salidas distintas; no sobrescribir experimentos.

## 6. Ejecutar pruebas y comprobar GitHub

Ejecutar desde raíz:
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json
python tools/f2_auditar_origen_iconos.py --iso-usa /RUTA/ISO_USA_PRIVADA.iso --reporte /tmp/f2-origen.json
cd patcher && go test ./... && cd ..
git diff --check

Si PPSSPP, ISO F1 u otras dependencias no existen, ejecutar todas las pruebas que sí correspondan, registrar bloqueos y nunca fabricar artefactos. Tras cada actualización comprobar GitHub Actions del HEAD FINAL y sus jobs. No declarar PPSSPP probado a partir de CI.

## 7. Fases posteriores y entrega OBLIGATORIA

F2 sigue ABIERTA hasta traza RAM/GE/VRAM verificada, QA multicontesto de 19 glifos y regresión F1 auténtica. F3: introducción todavía inglesa; localizar e integrar sin romper recursos. F4: modelar referencias/saltos e insertar con seguridad 4524 textos script aplazados. F5: recorrer aventura, niveles, combate, HUD, inventario, retratos, enciclopedia, guardado y carga. F6: generar BPS final, EXE Windows y QA integral. Mantener PR #7 DRAFT hasta finalizar todo.

Registrar modificaciones exactas, reporte de SHA por nuevo archivo ISO/BPS/PNG REAL (o NO GENERADO), pruebas estáticas/binarias/visuales/funcionales, funciones MIPS/GE verificadas y sus límites. Actualizar reports/ESTADO_CONTINUIDAD_PPSSPP.json y docs/reports de resultados. **Al acabar REESCRIBIR COMPLETAMENTE prompts/SIGUIENTE_TAREA.md con el siguiente prompt autónomo, mostrarlo al usuario e imponer en él que a su vez genere otro prompt al concluir. Repetir recursivamente hasta completar F2–F6 e integrar y verificar toda la traducción.**
