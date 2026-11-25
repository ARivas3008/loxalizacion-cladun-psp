# R37 — Últimos 1155: 328 nuevos textos verificados

Evidencia A independiente: las 1155 preimágenes de SCRIPT.DAT coinciden con la ISO USA original, 29805 bytes. Lotes 1000+155. Se reinsertaron 275 textos con 8–31 espacios y 53 con símbolos CP932; los 328 combinados conservan 51705 comandos, 46308 no textuales, SCRIPT.TBL y tres hermanos DSARC; IMY roundtrip exacto, cero offsets movidos. Los 53 conservan 65 tokens CP932 en su secuencia original. La representación visual y la semántica de símbolos no están certificadas en juego.

El perfil unificado se amplía de 7093 a 7421 (4073 SCRIPT, 3348 otros), 827 pendientes: 787 ASCII con exceso de capacidad, 19 con iconos y exceso, 11 multibyte no iconos, 10 con formatos o controles. No alterar el corpus ni los otros perfiles.

```bash
python tools/integrar_parche_seguro.py --iso /PRIVADO/USA.iso --candidate /PRIVADO/R37_7421.iso --report /PRIVADO/R37_7421.json --perfil-unificado --residuales-verificados
```

Este modo requiere la fuente compacta experimental y relleno hasta 31 espacios. No hay ISO acumulada nueva ni C en R37; el checkout local sigue bloqueado por DNS. Oficial histórico 3724/8248. CI inicial R36 45545120651 SUCCESS. El informe reports/R37_RESIDUALES_1155.json contiene hashes de las pruebas reales por bloque. No publicar ISO ni BPS propietario.
