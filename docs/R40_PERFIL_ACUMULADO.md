# R40 — Perfil acumulado 8188/8248

Se incorporan 492 propuestas de longitud fija, agrupadas en 3 bloques de 164. Reutilizan los 44 códigos de ligaduras existentes y conservan los tokens CP932 y formato. 417 textos ordinarios, 46 rótulos del interlocutor Mask adaptados como Careta, 29 textos con tokens especiales. Corpus maestro intacto. El ajuste Careta se limita al nombre de interlocutor; requiere revisión contextual en juego.

Evidencia A: comprobación independiente de 10549 bytes de preimagen sobre la ISO USA auténtica; 492 sustituciones en 196 bloques; 51705 comandos, 46308 no textuales idénticos, cero desplazamientos, SCRIPT.TBL y tres hermanos DSARC intactos. Se recompuso IMY con un codificador independiente (6 bloques cambiados, 2 idénticos), se creó una ISO privada diagnóstica que contiene exclusivamente los 492 cambios R40 y se comprobó que los restantes 348 recursos PSPFS son idénticos. BPS privado reconstruye exactamente la ISO diagnóstica (CRC32/SHA256). No distribuir ISO ni BPS que contenga recursos comerciales.

```bash
python tools/integrar_parche_seguro.py --iso /PRIVADO/USA.iso --candidate /PRIVADO/R40_8188.iso --report /PRIVADO/R40_8188.json --perfil-acumulado
```

Perfil experimental de código: 8188/8248 (99,27%), 4840 SCRIPT + 3348 otros; 60 pendientes. Las 60 preimágenes se autenticaron (49 ASCII, 11 multibyte); 57 exceden la longitud canónica mínima incluso con el diccionario actual; las otras 3 requieren revisión de símbolos o identificadores. Ninguno es el último comando de su bloque, por lo que no se puede usar el relleno final para aumentar sus bytes sin mover otro comando. No se integra un resultado que desplace eventos, elimine información o modifique un identificador sin prueba. CI inicial R39 45547083883 SUCCESS. El checkout local completo sigue bloqueado por DNS; la ISO acumulada y PPSSPP no se han ejecutado en R40. Oficial histórico 3724; no elevar métricas de release sin C.

Ver reports/R40_CONCISION_ACUMULADA.json y tools/r40_concision.py.
