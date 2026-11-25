# CLADUN ES — R35 autónomo: compilación real del nuevo perfil conservador acumulado

PR #7 DRAFT, rama integracion-eventos-segura-20261120. Verificar HEAD/CI, no force push ni merge. Leer docs/R34_CONSERVADORA_ACUMULADA.md y reports/R34_CONSERVADORA_ACUMULADA.json. El parcheador principal tiene el perfil --packs-verificados: 3724 F1 + 146 exactos + 1302 acolchados = 5172 (62,71% plan del código); 1448 IDs y offsets únicos, 360 bloques, huellas 1345572782/4017724493. Oficial histórico 3724; no ISO acumulada ni C en R34. CI inicial R33 45543211973 SUCCESS.

1. Checkout completo y original auténtica SHA b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. Ejecutar tests R34 y construir perfil único:
```bash
python tools/integrar_parche_seguro.py --iso /PRIVADO/USA.iso --candidate /PRIVADO/R35_5172.iso --report /PRIVADO/R35_5172.json --experimental-parcial --event-safe-only --packs-verificados
```
Confirmar 5172 cambios reales, 3076 diferidos, 1824 comandos textuales, 46308 no textuales exactos, 51705 comandos, 1625 scripts, cero offsets desplazados, fuente 19/2721, menú F1, recursos vecinos e ISO/BPS roundtrip. Si falta checkout o ISO, no inventar. 
2. PPSSPP oficial 1.20.4 A/B/A, todos gaps 1–7, menús, prólogo, tutoriales, combate, wrapping, signos, eventos, saves. Solo promover grupos sin regresión y evidencia C.
3. Después deduplicar 2002 ligaduras R25 contra 1448 ya seleccionados; 29 déficits R26, MIPS y QA F2–F6. No sumar dos veces ni confundir evidencia A/B/C. CI real y cero P0/P1. Al finalizar sustituir COMPLETAMENTE prompts/SIGUIENTE_TAREA.md por R36 autónomo, con obligación recursiva hasta 100% real T/G/R/Q.
