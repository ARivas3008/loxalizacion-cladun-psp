# R55 — 21 cajas/interlocutores y recompresión de 33 residuales

Evidencia A privada: 21 residuales +21 donantes, 27 comandos movidos (22 texto, 3 apertura 64, 2 separador 67), 0 fuera de los límites de la caja ampliada, 3 candidatos relativos numéricos, 0 absolutos/locales. Se reconstruyó además el perfil aislado completo de 33+35, 146 movimientos (104 no textuales), 31 candidatos relativos. Los 51.705 comandos conservan orden/opcode/ID, 46.308 no textuales byte exactos, 1.625 inicios y rellenos finales y SCRIPT.TBL intactos en ambos.

El compresor original excedió el slot de 699904 bytes por 460 bytes en el perfil de cajas. Se añade opción pendiente-literal (una referencia a literal en búfer solo se emite tras flush) y se elige menor de dos codificaciones por bloque; ambas decodifican exacto. Resultado: 699648 B (256 libres) para 21; 699692 B (212 libres) para 33. Dos ISO privadas de 305496064 B construidas, reabiertas y verificadas bit a bit fuera de descriptor y SCRIPT.SDT: 349 posiciones, 348 vecinos idénticos, ISO9660 intacta. No contienen fuente ni acumulada. SHA en JSON. No se publican.

Se añade constructor experimental privado independiente que construye la base R43 real con fuente, verifica sus 4866 cambios contra el plan, aplica únicamente 21 residuales y sus 21 donantes (guarda R52 exacta), preserva todos los recursos ajenos y crea candidato y reporte exclusivos. No se ejecutó este CLI íntegro localmente por falta de checkout (DNS); pruebas nuevas pendientes CI. 8235 sustituciones +1 disposición sin cambio (8236/8248 planificadas), no perfil oficial. No BPS, no PPSSPP, no release.

    python -m tools.r55_private_accumulated --iso /PRIVADO/USA.iso --candidate /PRIVADO/R55.iso --report /PRIVADO/R55.json --acepto-reubicacion-local

R54 CI 45710923129/45710933012 SUCCESS. 12 restantes requieren solución intradiálogo adicional o prueba de intérprete. No insertar IDs de página sin semántica verificada. Preservar prólogo, glifos y 44 ligaduras.
