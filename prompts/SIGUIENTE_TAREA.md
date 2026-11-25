# CLADUN ES — R47: solución de codificación fija o certificación MIPS del 0,40%

Verificar HEAD, CI, PR #7 DRAFT. R46 reprodujo independientemente los 78 cambios de R44 sobre ISO auténtica, con SHA idéntico; 33/33 residuales crecen y tienen comandos posteriores, 0/33 admisibles por la guarda fija, 2/33 incluso desbordan padding individual. La combinación mueve 2712 comandos (2221 no textuales). No promover.

1. Ejecutar tools.r46_verificar_residuales y suite completa. Compilar y auditar perfil acumulado 8214+1, y modo experimental 8247+1 por separado. Usar ISO privada. Verificar BPS rechazado para modo local.
2. Buscar una codificación alternativa sin mover offsets: optimizar diccionario de glifos compuestos preservando exactamente las 4866 traducciones previas, todas las métricas y símbolos originales; examinar el límite de anchura de cada slot. No sacrificar nombres, puntuación o glosario para cumplir un porcentaje.
3. Si no es viable, certificar referencias MIPS con PPSSPP oficial 1.20.4 y pruebas A/B/A de 24 bloques; priorizar 81 coincidencias R45. No confundir coincidencia con puntero.
4. Integrar solo tras guardas y evidencias auténticas. Mantener PR borrador, no merge, no force push, no activos comerciales. Sustituir este prompt por R48 autónomo con obligación recursiva hasta 100% real T/G/R/Q.
