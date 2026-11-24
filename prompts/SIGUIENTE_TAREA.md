# CLADUN ES — R32 autónomo: packs grandes y acumulación controlada

Meta ROMhacking 100% real. Rama integracion-eventos-segura-20261120, PR #7 DRAFT, no force push/merge. Verificar HEAD y CI. Leer docs/R31_BULK_PADDING.md, reports/R31_BULK_PADDING.json, tools/r31_bulk_padding.py, tools/r30_integrar_repeticiones.py, tools/r28_relocation_map.py, tools/r26_piloto_total_8248_privado.py, docs/R26_ROMHACKING_100_AUDITORIA_2026-11-24.md. R31 aplicó 608 nuevos (330 de 1 espacio, 278 de 2) más 146 exactos en ISO USA aislada SHA 4a9ec03611bd5a30dba28c1502de77f1c5cf288ace7e96b39fad99a948bfa39f; 347 PSPFS ajenos intactos, 51.705 offsets fijos, 46.308 no textuales exactos, 19 signos españoles, 2721 glifos intactos. 1.302 preimágenes auténticas verificadas; otros 694 con 3–7 espacios solo plan. No hay C, ni F1 acumulada. No publicar ISO ni datos comerciales.

1. Checkout completo; original SHA b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. Ejecutar test R31, construir packs one/two/long/all, comparar 608 digest y auditoría de offsets. Usar flags explícitos:
```bash
python tools/r31_bulk_padding.py --pack all
python -m unittest discover -s tests -p 'test_r31*' -v
python tools/r31_bulk_padding.py --pack all --allow-experimental-padding --iso-original /PRIVADO/USA.iso --candidate /PRIVADO/R32_5172_EXPERIMENTAL.iso
```
2. PPSSPP oficial 1.20.4 A/B/A: verificar padding final por familias de 1–7 espacios, anchura, salto de caja, puntuación, menús, tutoriales y escenas. No asumir los espacios invisibles: comprobar GE/VRAM y flujo. Si fallan, retirar por pack y buscar alternativas exactas. No promover sin C. Candidato F1+754=4.478; F1+1.448=5.172 solo si ejecutado. Mantener 3.724 oficiales hasta evidencia C.
3. Evaluar en lotes grandes las 2.002 ligaduras R25, deduplicar frente a R31 y no mezclarlas hasta prueba C de la fuente. Resolver 29 déficits y referencias MIPS de R26/R28; revisar de forma exhaustiva 4.524 diferidas. Completar QA, BPS y Win64 E2E, cero P0/P1. Ejecutar tests globales y CI, documentar A/B/C y actualizar cobertura cuatro áreas. Al terminar sustituir COMPLETAMENTE prompts/SIGUIENTE_TAREA.md por R33 autónomo con la misma obligación recursiva hasta 100% real T/G/R/Q.
