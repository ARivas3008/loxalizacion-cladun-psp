# R39 — Perfil acumulado 7696/8248

Se incorporan 176 propuestas de concisión, con repetidos de identidad exacta y abreviaturas puntuales de interfaz. Se excluyen 2 propuestas idénticas al original y las que no encajan o presentan riesgo semántico. No se modifica el corpus maestro.

Evidencia A: ensayo de 176 cambios y combinación de 603 con R37/R38 en SCRIPT.SDT original; 192 bloques, 51705 comandos, 46308 no textuales idénticos, cero desplazamientos, SCRIPT.TBL y tres hermanos DSARC intactos, IMY reversible.

```bash
python tools/integrar_parche_seguro.py --iso /PRIVADO/USA.iso --candidate /PRIVADO/R39_7696.iso --report /PRIVADO/R39_7696.json --perfil-acumulado
```

Perfil experimental de código: 7696 cambios, 4348 SCRIPT +3348 otros; pendientes 552 (512 ASCII, 19 iconos, 11 multibyte, 10 formatos). CI inicial R38 45546507217 SUCCESS. No se construyó la ISO acumulada completa ni se ejecutó PPSSPP; no aprobar release ni aumentar métricas oficiales de 3724 sin evidencia C. Revisar abreviaturas y concisión en contexto.
