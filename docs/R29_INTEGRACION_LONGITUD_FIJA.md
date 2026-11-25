# R29 — integración selectiva de longitud fija

Fecha 24/11/2026. HEAD previo 4af2b3597f6d5a11246702f1fa5edb5fb961d5be, push CI 45402396339 y PR CI 45402413341 SUCCESS. Se prioriza la solicitud de integrar lo que cumple seguridad binaria sin desplazar eventos.

Revisión de 90 propuestas R18/R20/R21: 31 del dictamen R19 apto estático, 3 R20, 19 R21 y 3 repeticiones con original y borrador exactamente iguales. Total 56. Se omiten propuestas ambiguas/rechazadas, p. ej. 000005, 000023, 000031, 000925, 000931, 000991, 001112. No hay ligaduras nuevas, relleno final ni modificación de la longitud. Los 56 IDs se cotejaron contra el blob canónico y se verificó geometría y CP932 A1–B3; no es aprobación visual/narrativa definitiva.

**A real, copia privada SCRIPT.DAT:** 56 sustituciones efectivas, 1.072 bytes distintos, 51.705 instrucciones reparseadas, 46.308 no textuales exactas, cero offsets movidos, SCRIPT.TBL intacto. SHA-256 de SCRIPT modificado: 372c8b96ad22e32c30468adc4ae0d5cf1d581fd866e7535273ce9b6b18a9b383. 16 son ASCII; 40 requieren el atlas español de 19 caracteres.

**A real, ISO privada ASCII:** se aplicaron 16 textos sobre ISO USA original, no sobre F1 acumulada. Se reconstruyeron 3 de 8 bloques IMY, se decodificaron los 8 y se verificaron las otras 3 secciones DSARC exactas. SCRIPT.SDT pasó de 699.624 a 700.020 B, se agregó al final sin mover recursos ajenos. 348 PSPFS idénticos. Todo el rango de ISO original byte-idéntico salvo 28 bytes de metadatos autorizados (tamaño ISO, tamaño DATA.DAT, índice SCRIPT.SDT); original SHA intacta. ISO candidata privada 306.196.480 bytes SHA 11f72494fbfe109772e8ceff91376936849c7f2934fafc5146525a0b6f108e24. No se publica ISO ni binarios originales.

**Integración acumulada implementada:** `tools/r29_integrar_longitud_fija.py` construye la base canónica de 3.724, aplica los 56 textos exactos, exige 51.705 comandos y cero movimientos mediante auditor R24, conserva la fuente existente y verifica los 348 recursos no SCRIPT contra la base. Objetivo acumulado 3.780 (45,83 %), NO ejecutado en el contenedor por falta de checkout completo. Los 40 con signos españoles no se aplican a la ISO USA sin fuente. No cambiar corpus canónico ni modo estable; el integrador privado selecciona las alternativas sin alterar el original. No publicar parche final. PPSSPP 1.20.4 no disponible; ninguna aprobación C nueva.

```bash
python tools/r29_integrar_longitud_fija.py
python -m unittest discover -s tests -p 'test_r29*' -v
python tools/r29_integrar_longitud_fija.py --iso-original /PRIVADO/Cladun_USA.iso --candidate /PRIVADO/R29_3780_EXPERIMENTAL.iso
```

Porcentaje histórico oficial: 3.724/8.248, 45,15 %. La aprobación de 56 estática no equivale a promoción oficial ni prueba C; no contabilizar 16 dos veces. Informe numérico: reports/R29_INTEGRACION_LONGITUD_FIJA.json. 
