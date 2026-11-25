# F2 — Comparador A/B de capturas X11 con procedencia y ROI, 23/11/2026

**F2 ABIERTA.** Este relevo ejecutó inspección auténtica de los dos archivos ISO privados ya extraídos, implementó comparador A/B de X11 y probó casos sintéticos. **No ejecutó PPSSPP 1.20.4 ni obtuvo nuevas capturas de habilidades, GPU/GE o RAM/VRAM.** Conservar la separación: A original real, B tests, C runtime genuino.

## A. Cotejo directo de las dos ISOs comerciales privadas

En esta sesión se leyeron físicamente, por bloques, los archivos existentes en /mnt/data/cladun_private_20261123 (externos al repositorio):

- USA original: 305.496.064 bytes, SHA-256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f.
- Sonda CLUT2: 305.496.064 bytes, SHA-256 b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa.
- Comparación integral, bloque a bloque: exactamente 3 diferencias absolutas, offsets 114744872 (249→255), 114744873 (251→0), 114744874 (249→255). El archivo original no se modificó.

No equivale a prueba de carga GPU TUIKA. La verificación completa de 349 PSPFS/27 DSARC consta en docs/F2_GE_ONLY_WEB_SOCKET_SIN_FRAMEBUFFER_2026-11-23.md y no se atribuye nuevamente como cómputo de este relevo.

Se intentó descargar el AppImage desde la publicación oficial PPSSPP v1.20.4: https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4. El repositorio oficial declara para el AppImage Linux x86_64 un tamaño de 50.689.748 bytes, coherente con el hash histórico 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21; la descarga al contenedor falló. Ningún AppImage nuevo fue autenticado ni ejecutado aquí.

## B. Nueva herramienta con comparaciones verificables, solo metadatos fuera de Git

Se creó tools/f2_cotejar_x11_tuika.py, que **NO** acepta manifiestos de gpu.buffer.screenshot ni dumps GE-only. Acepta exclusivamente los manifiestos v1 producidos por tools/f2_x11_ppsspp_procfs_capture.py, dos PNG reales del tamaño de ventana X11 960×544 y las dos ISOs privadas USA y sonda con hashes canónicos.

Comprueba que:
- los manifiestos están fuera de Git, separados en dos directorios;
- roles, SHA de ISO, tamaños, nombre PNG sin traversal, formato y SHA de PNG coinciden;
- la ventana X11 declara PID positivo, dimensiones 960×544, título Cladun y testigos /proc con starttime e inodo abierto antes/después;
- la salida privada no existe previamente y solo contiene números, SHA y metadatos, sin PNG ni bytes ISO;
- compara RGB del fotograma entero y opcionalmente ROI x,y,ancho,alto, sin remuestrear, usando la misma función de candidatos magenta que el comparador del framebuffer WS.

El informe marca obligatoriamente false: visual_scene_alignment_proven, gameplay_event_proven, psp_framebuffer_used, emulated_frame_timing_verified, loaded_iso_identity_proven, tuika_texture_gpu_identity_proven y mips_ram_ge_vram_pipeline_proven. Los testigos /proc leídos de un JSON son **declaraciones**, no una repetición independiente de la observación. La escena se introduce mediante --escena como etiqueta aportada por el operador, NO como prueba de sincronización. El splash SYSTEM PRiSM contenía 1.152 píxeles magenta naturales y dos PNG A/B idénticos en una sesión anterior; el comparador debe reflejar cero diferencias, sin declarar la sonda funcional.

tests/test_f2_cotejar_x11_tuika.py incorpora **16 tests sintéticos**, que aprobaron localmente (16/16, 1.101 s) usando un **shim local sintético** para la interfaz auxiliar f2_cotejar_capturas_tuika; dicho shim NO se publicó. El CI de GitHub deberá correr los mismos tests con el helper REAL del repositorio; no atribuir los tests locales al runtime PPSSPP.

Comandos en checkout autentificado, SOLO tras capturar USA y sonda en escena idéntica:

    python tools/f2_cotejar_x11_tuika.py \
      --manifest-usa /PRIVATE/USA_X11/session.json \
      --manifest-sonda /PRIVATE/SONDA_X11/session.json \
      --iso-usa /PRIVATE/USA_original.iso \
      --iso-sonda /PRIVATE/TUIKA_sonda.iso \
      --escena HABILIDAD_CONFIRMAR_VISUALMENTE \
      --roi 120 60 720 420 \
      --reporte-privado /PRIVATE/TUIKA_X11_AB_INFORME_NUEVO.json

La ROI es ejemplo, no coordenada medida; sin --roi el cotejo abarca la ventana completa. NO usar el comparador WS tools/f2_cotejar_capturas_tuika.py con PNG X11. Ni un pixel magenta nuevo basta para atribución causal: exige escena realmente equivalente y traza GE/RAM/CLUT auténtica.

## C. Estado runtime y pasos prioritarios

No hay nuevas capturas X11, fotogramas framebuffer PSP, comandos GE, PCs MIPS ni direcciones RAM/VRAM de este relevo. El AppImage oficial PPSSPP no fue descargable desde el contenedor, aunque las ISOs originales sí están presentes. No es válido usar el splash como muestra de habilidad, ni los PNG X11 como framebuffer WebSocket.

F2 necesita alcanzar una escena de habilidades/trampas/combate en PPSSPP auténtico y reproducirla con USA/sonda (arranques independientes), WS 24192 autenticado por el mismo PID y fd ISO, pulsaciones con release confirmado, X11 A/B verificable y GE-only real. Con esos insumos, ejecutar el nuevo comparador y herramientas tools/f2_ge_dump_1204.py / f2_ram_provenance_1204.py para atribuir textura, sin elevar direcciones candidatas a certeza. Verificar 19 glifos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō en varios contextos y paletas; mantener white_new_ink=False.

F3 avanzó simultáneamente en commit histórico cffd12b0550ac47f92980ebeb195fe1afabce9ab: tools/f3_anime_topologia.py encontró 231 firmas IMY en ANIME000.IDT (136 tipo 0x00/95 tipo 0x02), 24 en ANIME001.LDT y 0 en ANIME002.LDT; los 95 tipo 0x02 carecen de decodificador demostrado. Ese progreso es independiente de F2 y NO demuestra origen de letras del prólogo. Mantener demo1001 85 eventos bloqueados y F4 4.524 cambios SCRIPT.DAT aplazados bajo --event-safe-only, 9.237 corpus, 2.721 glifos originales; F5 y F6 siguen abiertas.

No subir ISO, BPS, EBOOT, FONT, IMY, dumps, PNG comerciales al Git. Mantener PR #7 OPEN/DRAFT, y la obligación de reemplazar íntegramente prompts/SIGUIENTE_TAREA.md en cada relevo.
