# R38 — Perfil acumulado único: 7520 de 8248

R38 agrega 99 propuestas de concisión de inserción (sin modificar el corpus maestro). Se compararon contra el original inglés y el borrador canónico; las propuestas que no encajan o presentan riesgos semánticos evidentes se descartaron. El overlay TSV está anclado por SHA256 y su plan coincide con la preimagen de ISO auténtica y la reproducción canónica independiente.

Pruebas privadas A ejecutadas: 99 nuevos textos en SCRIPT.DAT, más ensayo combinado de los 328 R37 y 99 R38 = 427 textos en 139 bloques, 51.705 comandos, 46.308 no textuales exactos, cero offsets movidos, SCRIPT.TBL y tres hermanos DSARC intactos, IMY roundtrip exacto. No se construyó la ISO completa acumulada R38 ni se ejecutó PPSSPP; checkout local bloqueado por DNS. La cobertura de código es 7520/8248 (91,17%), no un release certificado.

## Compilación privada única
```bash
python tools/integrar_parche_seguro.py --iso /PRIVADO/USA.iso --candidate /PRIVADO/R38_7520.iso --report /PRIVADO/R38_7520.json --perfil-acumulado
```
Activa todas las etapas verificadas anteriores: 3724+146+1302+1921+275+53+99, 4172 cambios SCRIPT y 3348 otros. Mantiene rutas anteriores de respaldo. La fuente compacta y la presentación del relleno, ligaduras y símbolos siguen pendientes de QA visual y contextual. No publicar ISO/BPS ni recursos comerciales. Pendientes 728: 688 ASCII overflow, 19 iconos overflow, 11 multibyte no iconos y 10 formatos. CI inicial R37 45545886400 SUCCESS. Ver reports/R38_CONCISION_ACUMULADA.json.
