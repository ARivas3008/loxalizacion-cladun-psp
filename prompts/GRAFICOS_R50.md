# G-R50 — integración de gráficos con el prólogo canónico del usuario

**Fuente obligatoria:** `traduccion/PROLOGO_GRAFICO_ES.txt`, `reports/G_R50_PROLOGO_CANONICO.json`, `docs/G_R50_PROLOGO_CANONICO.md`. La redacción R49 queda obsoleta; no sustituir palabras del usuario ni añadir puntuación por renglón. Usar únicamente el ZIP privado R50 con SHA-256 785dbceeda29b489e3373ee5427de1a01b422f68e45bedd1fe3aa9fc5e6925b5. Comprobar con tools/g_r50_prologo_reinsercion.py; repetir 53 recursos con reproducir_r49.py incluido en dicho ZIP. PIC0 usa las últimas tres líneas del prólogo. No aceptar R49 antiguo.

1. PPSSPP oficial 1.20.4 A/B/A del diagnóstico real R50 de slot fijo; verificar CLUT, legibilidad, escena inicial, sin inventar capturas.
2. Reconstruir contenedores IDT/LDT, SYSGRA DSARC, SYS.DAT2, MPB e ISO PNG, resolver los crecimientos sin romper referencias; PIC0 crece 7410 B. Probar recursos ajenos byte-exactos y conservar 17 pares de créditos. No aplicar offset absoluto a ISO reconstruida. Integrar con perfil ROMhacking conservador solo tras guardas y pruebas.
3. Revisar 309 superficies de paleta/escena, 4 condicionales, 2 abreviaturas y 7 fuentes; nuevos textos solo con contexto y glosario.
4. Registrar A/B/C reales, actualizar QA, mantener PR #7 DRAFT, sin merge ni force push, sin publicar activos comerciales; regenerar G-R51 recursivo hasta cierre real. No confundir 53/53 objetivos conocidos con cierre de todo el universo gráfico.
