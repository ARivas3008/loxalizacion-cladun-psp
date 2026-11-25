# CLADUN ES — R38 autónomo: 827 pendientes y validación acumulada

Rama integracion-eventos-segura-20261120; PR #7 DRAFT. Verificar HEAD/CI; no merge ni force push. Leer docs/R37_RESIDUALES_1155.md y reports/R37_RESIDUALES_1155.json. R37 verificó A las 1155 preimágenes de ISO auténtica en 1000+155; escribió 275 rellenos 8–31 y 53 textos CP932 preservando 65 tokens, total 328 en un SCRIPT.SDT auténtico, cero offsets movidos, 51705 comandos, 46308 no textuales intactos, tres hermanos y tabla intactos, IMY roundtrip. El perfil principal --perfil-unificado --residuales-verificados incorpora 7421 cambios (4073 SCRIPT +3348 otros); 827 pendientes. CI inicial R36 45545120651 SUCCESS. No ISO acumulada nueva ni C; oficial histórico 3724.

1. Checkout completo, ISO auténtica SHA b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. Ejecutar tests y construir privada con:
```bash
python tools/integrar_parche_seguro.py --iso /PRIVADO/USA.iso --candidate /PRIVADO/R38_7421.iso --report /PRIVADO/R38_7421.json --perfil-unificado --residuales-verificados
```
Verificar 7421 efectivos, 827 diferidos, 4073 comandos modificados, 51705 comandos, 46308 no textuales, 1625 scripts, 349 PSPFS, fuente 2721+19+44, F1, BPS roundtrip. No publicar ISO, BPS ni recursos comerciales.
2. Resolver 827 en bloque único: 787 ASCII, 19 iconos overflow, 11 multibyte no iconos y 10 formatos. De 787 ASCII, 317 déficit 1, 133 déficit 2, 111 déficit 3, resto mayores. Mantener diccionario 44 existente: buscar propuestas editoriales naturales de longitud exacta o combinación de ligaduras, sin alterar corpus, comprobar significado/contexto, controles e iconos. Priorizar 561 déficits 1–3. Auditar preimágenes y combinaciones contra ISO real; solo incorporar soluciones que pasen. No inventar C.
3. PPSSPP oficial 1.20.4 A/B/A: relleno 8–31, iconos CP932, 44 ligaduras, menú F1, prólogo, tutorial y combate, saves y eventos. Separar A/B/C, sin promover oficial sin C. Resolver F2–F6 y cero P0/P1. Al terminar sustituir COMPLETAMENTE prompts/SIGUIENTE_TAREA.md por R39 autónomo con obligación recursiva hasta 100% real T/G/R/Q.
