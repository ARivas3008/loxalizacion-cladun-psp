# R20 — Exposición estructural de referencias por crecimiento de texto

Nuevo analizador solo lectura: `tools/f4_r20_relocation_exposure.py`. Para cada comando textual cuenta comandos textuales y no textuales que le siguen **dentro del mismo bloque**. Si se aumenta o reduce el tamaño del comando y se reconstruye la secuencia contigua, los offsets posteriores cambian; que los comienzos de bloques puedan conservarse mediante padding NO elimina ese riesgo.

**A, cálculo independiente sobre SCRIPT.DAT original autenticado:** 1625 bloques, 51705 comandos, 5397 comandos textuales repartidos entre 587 bloques. Ninguno de los 5397 textos es el último comando de su bloque. Todos tienen al menos **2 comandos posteriores** (máximo 1025; mediana 67). Cada bloque termina con opcode 0x08. La suma de exposiciones de comandos posteriores, contando cada posible edición por separado, es 758170. Estas exposiciones NO son 758170 referencias MIPS verificadas ni 758170 comandos distintos.

**Conclusión:** no existe justificación estructural para habilitar automáticamente las 4524 sustituciones de tamaño variable. Es necesaria ingeniería inversa del dispatcher, referencias de offsets y pruebas PPSSPP auténticas. `--event-safe-only` sigue activo. La herramienta no escribe ni extrae recursos y emite solo métricas agregadas. **B:** cinco pruebas sintéticas positivas/negativas en `tests/test_f4_r20_relocation_exposure.py`. **C:** no realizada.

Reproducir:
```bash
python -m unittest discover -s tests -p 'test_f4_r20_relocation_exposure.py' -v
python tools/f4_r20_relocation_exposure.py --iso-original /PRIVADO/Cladun_USA_original.iso
```
