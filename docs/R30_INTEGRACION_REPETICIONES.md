# R30 — 90 nuevas reinserciones de longitud fija

CI R29: push 45403327157 y PR 45403339388 SUCCESS (HEAD 058dafedc3e3c294c4c5b58eb90c17aaf1749e3e). Se recuperó el corpus canónico y se revisaron 12 equivalencias exactas de inglés+borrador español: 52 avisos de acceso a mazmorras, 6 consultas informativas, 17 interjecciones/preguntas breves, 4 accesos a taberna, 3 advertencias y 8 fragmentos de ayuda. Los 90 IDs son disjuntos del lote R29. No se admitió una alternativa de tartamudeo con énfasis añadido. Se mantienen todas las longitudes, sin espacios finales añadidos ni ligaduras nuevas. El aviso de mazmorra omite el adverbio «ahora» para conservar el límite, pero mantiene el anuncio de acceso. Aprobación contextual y visual pendiente.

## Evidencia auténtica privada
- Aplicación acumulada de 146 (56+90) en copia de SCRIPT.DAT: 3.192 bytes distintos, 51.705 comandos, 46.308 no textuales intactos, 0 offsets movidos, tabla original intacta. SHA 2d0e2997de9adb850174d6dfc596bb6310f78aa49dcf9f4216f963468c65fa21.
- ISO original USA con 26 textos ASCII (16+10): SHA 028d697d40385a8b88baae366bf849217de9099ce1dd3c83349f0ddede8f07df, 306.196.480 B. SCRIPT.SDT 700.148 B, append-only. 348 PSPFS ajenos exactos, 3 DSARC hermanos exactos, 8 bloques IMY decodificados, 4 recompuestos. Todo el rango original igual salvo 28 bytes autorizados de metadatos. Fuente sin modificar; ISO original conserva SHA histórica.
- Los otros 120 requieren la fuente española existente. No se produjo una candidata acumulada de 3.870 ni se ejecutó PPSSPP. No se suben activos comerciales.

## Integración reproducible
`tools/r30_integrar_repeticiones.py` extiende el constructor privado R29 con 12 reglas estrictas (coincidencia de ambos textos, bytes originales y cantidad exacta) y comprobación de IDs/offsets disjuntos. R29.run acepta plan inyectado manteniendo por defecto su selección original. 7 pruebas nuevas para CI. El modo estable y corpus canónico no cambian.

```bash
python tools/r30_integrar_repeticiones.py
python -m unittest discover -s tests -p 'test_r30*' -v
python tools/r30_integrar_repeticiones.py --iso-original /PRIVADO/Cladun_USA.iso --candidate /PRIVADO/R30_3870_EXPERIMENTAL.iso
```

Oficial: 3.724/8.248 = 45,15%. Acumulado experimental objetivo: 3.870/8.248 = 46,92%; 146 añadidos en SCRIPT, 26 en ISO aislada, sin doble conteo. Ningún PASS C ni autorización de publicación. Ver reports/R30_INTEGRACION_REPETICIONES.json.
