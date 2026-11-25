# F2 — WebSocket sin pérdida de eventos y breakpoints bajo control (21/11/2026)

**F2 ABIERTA:** no se dispone del AppImage oficial PPSSPP 1.20.4 ni de una ISO F1 canónica autenticada en esta sesión. Se intentó GitHub desde la terminal y por dirección IP: ambos caminos bloqueados; el conector de GitHub sí permitió lectura y escritura segura de código. No se ejecutó ningún juego en PPSSPP ni se capturaron PNG/dumps gráficos nuevos.

## 1. QA sobre ISO USA realmente proporcionada

Se comprobó el archivo privado de 305496064 bytes, SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. El IMY comprimido KITAJIMA_KARI.IMY, offset absoluto 114723840, tamaño 2480, volvió a arrojar `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`. La auditoría raster leyó las 6 páginas FONT.ARC originales, reexaminó 19 glifos nuevos y 2721 existentes, con 100 texels de tinta optativa; el reporte privado tiene SHA-256 `88edb8a2cf1a920f1ff7480cbe4b06f44d5441a1183720b71a07b393a49bfb80`. Ninguno de estos análisis implica representación en PPSSPP.

## 2. Corrección comprobable de WebSocket

Se estudió `SteppingBroadcaster.cpp`, `CPUCoreSubscriber.cpp`, `MemorySubscriber.cpp`, `BreakpointSubscriber.cpp`, `Core/Core.cpp` y `Core/Debugger/Breakpoints.cpp` del tag oficial PPSSPP 1.20.4. `cpu.stepping` y `cpu.resume` son notificaciones asíncronas sin ticket; pueden recibirse mientras llega una respuesta con ticket. `tools/f2_ppsspp_ws_1204.py` conserva estos broadcasts en una cola acotada, permite consumirlos posteriormente, invalida eventos ya vistos del tipo de una nueva notificación y rechaza errores asíncronos en lugar de ocultarlos. Cuatro tests sintéticos nuevos comprueban ese orden.

## 3. Protección de puntos de vigilancia

PPSSPP 1.20.4 expone `memory.breakpoint.list` para enumerar puntos vigilados; antes de instalar el propio, `tools/f2_ram_provenance_1204.py` comprueba que no exista un rango superpuesto y falla de forma conservadora ante datos ambiguos. Asimismo, `Core_Break(BreakReason::MemoryBreakpoint, start)` y `BreakReasonToString` prueban que la pausa atribuible a nuestra vigilancia requiere `reason == "memory.breakpoint"` y `relatedAddress == start`. Una pausa ajena, incluso con dirección coincidente, permanece detenida y no se atribuye al recurso KITAJIMA. Se añadieron 6 tests sintéticos nuevos. El API no serializa cambios simultáneos de otro cliente; usar una única sesión de depuración.

## 4. Pruebas y límites

Los commits `4cc319092b16b1aee528c4359d0dd5b7da25f178` y `a3d246b198a74ca8bcafcdc42534e76e3a97ae05` pasan ambos workflows de GitHub Actions del último commit: **209 pruebas Python**, comprobación de integridad del corpus, pruebas Go y compilación pública Windows (sin BPS). No se pudo ejecutar `git fetch`, batería completa Python/Go local ni arrancar PPSSPP por restricción de red/entorno. **NO PROBADO:** MIPS→GE→VRAM, HUD, combate, tutoriales, QA visual multicontesto de 19 glifos ni regresión F1 a 960×544. Mantener `white_new_ink=False`, `--event-safe-only`, PR #7 DRAFT y 4524 cambios SCRIPT aplazados.

Informe: `reports/RESULTADO_F2_WS_BREAKPOINT_2026-11-21.json`. Relevo: `prompts/SIGUIENTE_TAREA.md` (reescritura recursiva obligatoria).
