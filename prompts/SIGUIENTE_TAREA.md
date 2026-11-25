# CLADUN ES — R40 autónomo: 552 restantes y validación acumulada

Rama integracion-eventos-segura-20261120; PR #7 DRAFT; no merge ni force push. Verificar HEAD/CI. Leer docs/R39_PERFIL_ACUMULADO.md, reports/R39_CONCISION_ACUMULADA.json, tools/r39_concision.py y traduccion/propuestas/R39_CONCISION.tsv. R39 escribió 176 textos auténticos y revalidó 603 combinados R37–R39, 192 bloques, 51705 comandos, 46308 no textuales intactos, cero offsets movidos, tabla y tres hermanos DSARC exactos, IMY roundtrip. Perfil --perfil-acumulado = 7696/8248 (93.31%), 4348 SCRIPT y 3348 otros. Oficial histórico 3724; C no ejecutada. CI inicial R38 45546507217 SUCCESS.

1. Checkout completo e ISO privada USA SHA b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. Ejecutar unittest y construir privada:
```bash
python tools/integrar_parche_seguro.py --iso /PRIVADO/USA.iso --candidate /PRIVADO/R40_7696.iso --report /PRIVADO/R40_7696.json --perfil-acumulado
```
Exigir 7696 efectivos, 552 diferidos, 4348 textos SCRIPT, 51705 comandos, 46308 no textuales exactos, 1625 scripts, 349 PSPFS, 2721+19+44 glifos, F1 y BPS roundtrip. No distribuir ISO/BPS/recursos comerciales. No inventar.

2. Resolver 552 en lote único: 512 ASCII overflow, 19 iconos, 11 multibyte, 10 controles/formato. Priorizar repetidos y déficits pequeños; los 46 casos de Máscara/Mask de 4 bytes necesitan una solución natural (no truncar por defecto), revisar el contexto del nombre. Conservar diccionario de 44, corpus maestro, referentes, signos, números, símbolos CP932 y controles. Revisar fragmentos vecinos. Rechazar sustituciones idénticas, pérdidas semánticas y solapamientos. Probar cada lote en SCRIPT auténtico, recomprimir IMY, acumular con 603 previos, y añadir al mismo --perfil-acumulado con hashes, guardas y CI. Si hace falta revisar una estrategia de ligaduras alternativa, preservar todos los 4348 registros previos y sus glifos; no contar un prototipo sin prueba.

3. PPSSPP oficial 1.20.4 A/B/A: fuente compacta, símbolos, rellenos 1–31, ligaduras, menú, tutorial, prólogo, combate, saves, escenas. Separar evidencia A/B/C; no elevar oficial sin C. Cero P0/P1. F2–F6 pendientes. Al finalizar reemplazar COMPLETAMENTE prompts/SIGUIENTE_TAREA.md por R41 autónomo con obligación recursiva hasta 100% real T/G/R/Q.
