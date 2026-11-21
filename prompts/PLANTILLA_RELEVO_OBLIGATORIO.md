# Plantilla obligatoria para prompts de relevo de Cladun ES

**Regla:** al terminar CADA fase, rellenar esta plantilla con hallazgos **reales** y reemplazar/sobrescribir `prompts/SIGUIENTE_TAREA.md`. Presentar el nuevo prompt entero al usuario, además de guardar el commit en GitHub. Cada nuevo prompt debe obligar a escribir otro al terminar la fase posterior. No dejar hashes/capturas/rutas inventadas.

---

Actúa como ingeniero de localización PSP, formatos DSARC/IMY/PSPFS, QA en PPSSPP y parcheador BPS/Go. Continúa Cladun USA con cambios comprobables, sin cambiar opcodes de eventos, referencias no modeladas, sprites, retratos, tiles ni recursos ajenos. **Al terminar este trabajo, genera, sube a GitHub y muestra otro PROMPT AUTÓNOMO con la misma obligación de relevo** y actualiza `reports/ESTADO_CONTINUIDAD_PPSSPP.json`.

Repositorio: `https://github.com/ARivas3008/loxalizacion-cladun-psp`.
Rama/PR actuales: [RAMA, URL] · último commit SHA confirmado: [SHA].
Documentación obligatoria: `AGENTS.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, [INFORME DE ETAPA ACTUAL].

**Estado ya demostrado (no conjeturas):** [QUÉ FUNCIONA EN PPSSPP, VERSIÓN, HASHES SHA-256 DE ISO/BPS, TESTS CORRIDOS, CAPTURAS/LOGS].
**Problemas pendientes:** [IDS, RECURSOS, SÍNTOMA, PASOS PARA REPRODUCIR, SEPARAR CAUSA CONFIRMADA DE HIPÓTESIS, PRIORIDAD].
**Tarea siguiente concreta [F#]:** [UNA ACCIÓN Y ALCANCE DEFINIDOS].
**Por qué:** [FALLO Y RIESGO].
**Dónde:** [CÓDIGO, CSV, IDs, RECURSO DENTRO DE DATA.DAT].
**Cómo:** [ANÁLISIS, PRUEBAS AISLADAS, CAMBIOS MÍNIMOS; ORIGINAL USA COMO CONTROL; COMANDOS REPRODUCIBLES].
**Criterios:** [CERO DESFASES/ERRORES EN RENDER, INTEGRIDAD, LOGS, HASHES Y CAPTURAS EN PPSSPP; SI NO SE LOGRA, BLOQUEO DEMOSTRADO].
**Restricciones:** [NO PUBLICAR ISO NI ASSETS, NO QUITAR GUARDAS DE EVENTOS, NO MODIFICAR IDS/ORIGINALES; NO INVENTAR VALIDACIÓN].
**Entregables:** [GITHUB COMMIT/PR + INFORME + CAPTURAS REALES + TESTS + ESTADO JSON + **NUEVO** PROMPT EN `prompts/SIGUIENTE_TAREA.md` QUE TAMBIÉN OBLIGUE A CREAR OTRO PROMPT].

Si la fase no ha terminado, el nuevo prompt debe continuar el problema bloqueante con la siguiente prueba de causa más útil. No avanzar solo para completar una lista.

---
**Ver guía y plan de fases:** `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`.
