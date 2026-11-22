# Cladun ES — F2: depurador WebSocket, pausa GPU y sonda RAM (21/11/2026)

ESTADO: F2 ABIERTA. Los avances corresponden a código, pruebas sintéticas en CI y autenticación binaria REAL de la ISO USA. NO se ejecutó PPSSPP real durante este relevo; no hay nuevos PNG, capturas de desktop, dumps GE reales, PCs de iconos, VRAM ni regresión F1 real.

## Hallazgo y corrección en capturas

En el tag oficial hrydgard/ppsspp v1.20.4, Core/Debugger/WebSocket/GPUBufferSubscriber.cpp, GenericStreamBuffer exige CPU detenida (CORE_STEPPING_CPU) o GPU stepping. El cliente previo solicitaba gpu.buffer.screenshot con CPU en marcha y el emulador habría contestado Neither CPU or GPU is stepping.

tools/f2_ppsspp_ws_1204.py ahora: (1) inicia gpu.record.dump ANTES de pausar, con CPU corriendo para grabar el siguiente frame; (2) consulta cpu.status; (3) pide cpu.stepping mediante notificación asíncrona; (4) espera el evento de broadcast y confirma la pausa; (5) lee cada framebuffer; (6) usa cpu.resume solo cuando él mismo pausó. Preserva pausas establecidas previamente por otra sesión. Incluye timestamps de ticks y tamaños del framebuffer. Esta captura PSP no es una captura de la ventana X11 960x544, por lo que NO valida las cifras F1 756/764. Se corrigieron también los nombres de los dumps: ESCENA_GE_PRIVATE.dump.

Se añadieron seis pruebas sintéticas de los estados CPU / recorder, incluido cierre seguro ante PNG inválido. En GitHub Actions HEAD 51c4f9a956f92784aeeff8b2d7f44baa9ac54424 se ejecutaron 183 pruebas Python OK. No son PPSSPP funcional real.

## Autenticación real y sonda RAM de solo lectura

Se confirmó otra vez el SHA original USA: 305496064 bytes, SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. La firma comprimida exacta KITAJIMA_KARI.IMY, offset ISO absoluto 114723840 (0x06D68C00), longitud 2480 y SHA256 0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190 se extrajo en memoria y cotejó con su hash; NO se distribuyó.

La nueva herramienta tools/f2_ram_provenance_1204.py permite SOLO la verificación de origen sin emulador:
python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/f2-origen-nuevo --solo-origen

Se ejecutó este modo realmente sobre la ISO autenticada. Reporte privado SHA256 e8604ef2cf0303b1fa29b6c986f916528a36845d0846d4c0df396c6e2facdbb9, con actual_ram_trace=NOT_EXECUTED y mips_ge_vram_chain_proven=false.

Con PPSSPP REAL disponible, --scan-ram busca la firma completa en PSP RAM 0x08800000..0x0A000000, usa bloques 65536, solapamientos correctos y marca páginas ilegibles. --watch-address solo admite una dirección RAM observada y agrega breakpoint para registrar PC MIPS, motivo, desensamblado y GPR, con limpieza controlada. Ni un hit RAM ni una pausa de CPU prueban por sí solos GE/VRAM; contrastar con gpu.record.dump y con controles positivo/negativo, además de HUD/tutorial/combate.

Diez tests sintéticos de esta nueva herramienta PASARON localmente y en GitHub Actions. Ambos jobs del commit ee83ed5a4ff7cdcb8a60b84436db82a6613be009 finalizaron SUCCESS; 193 pruebas Python, más pruebas Go y compilación pública Windows sin BPS. La descarga del AppImage oficial no fue posible por DNS de github.com en el runtime; no había ISO privada F1. El acceso Git se hizo con el conector, nunca se declaró git fetch ejecutado.

## Invariantes e historial

No se editaron los archivos canónicos del corpus, el integrador ni white_new_ink=False. Se conservaron --event-safe-only y PR #7 DRAFT. Precedentes F1: ventana 960x544, 756 interiores/~764 exteriores. Precedentes F2: 2721 originales +19 glifos A1-B3, 100 texels de tinta index15→1 solo optativa; 349 PSPFS, 26 vecinos DSARC, 51705 comandos SCRIPT, 46308 no textuales, 1625 inicios y 4524 textos de script aplazados. Estas cifras históricas NO son validación funcional nueva.

Documento correlativo: reports/RESULTADO_F2_RELEVO_CAPTURA_RAM_2026-11-21.json. Prompt sucesivo: prompts/SIGUIENTE_TAREA.md. F2 permanece ABIERTA y F3-F6 pendientes.
