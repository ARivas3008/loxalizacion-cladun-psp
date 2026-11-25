# R34 — Perfil conservador acumulado (5.172 / 8.248)

Se integran al código principal 146 propuestas R29/R30 y los 1.302 textos R31–R33, en una sola reconstrucción de SCRIPT.SDT junto a F1. Se conserva la ruta histórica como opción de recuperación. La nueva ruta exige corpus canónico, fuente A1–B3, modo experimental parcial y offsets fijos; rechaza duplicados, preimágenes, longitudes, solapamientos y fingerprints incorrectos. 1.448 IDs adicionales únicos, 360 bloques, 41.487 bytes de preimagen; FNV32 combinado 4017724493, preimágenes 1345572782. 1.824 comandos textuales en el plan final, 3.348 cambios en otros recursos, 3.076 diferidos. El auditor binario exige 46.308 no textuales idénticos y cero offsets movidos antes de escribir la candidata. Los recursos F1 no se sustituyen por la ISO diagnóstica R33.

```bash
python tools/integrar_parche_seguro.py --iso /PRIVADO/USA.iso \
  --candidate /PRIVADO/R34_CONSERVADORA_5172.iso \
  --report /PRIVADO/R34_CONSERVADORA_5172.json \
  --experimental-parcial --event-safe-only --packs-verificados
python -m unittest discover -s tests -p 'test_r34*' -v
```

Evidencia B: reconstrucción independiente del plan canónico completo mediante conector GitHub, 1.448 IDs/offsets únicos y huellas comprobadas. Evidencia A previa: pruebas aisladas R29–R33. **No se ha construido una ISO acumulada nueva ni ejecutado PPSSPP en R34**: checkout local bloqueado por DNS. El 62,71 % es cobertura del nuevo perfil del código, no liberación aprobada. Oficial conservadora histórica 3.724/8.248. No publicar ISO ni BPS diagnóstico. Próximo: generar y certificar la acumulada y posteriormente deduplicar y comprobar las 2.002 ligaduras R25 sin desactivar las guardas.
