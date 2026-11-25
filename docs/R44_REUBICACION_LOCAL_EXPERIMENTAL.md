# R44 — Cobertura del objetivo 8248/8248 por reubicación local EXPERIMENTAL

CI de R43 45656364906 SUCCESS. Perfil conservador de código: 8214 sustituciones + 1 disposición sin cambio = 8215/8248 (99,60%). Los 33 restantes se codificaron sin truncar nombres ni eliminar signos de apertura. Se redistribuyen 40 bytes de crecimiento: 22 recuperados de 18 traducciones vecinas (mismo texto y código existente) y 18 del padding original. La ISO USA auténtica fue reescrita en un diagnóstico PRIVADO de 78 sustituciones: 21 R42, 5 R43, 1 reparación, 33 nuevos y 18 donantes. NO es la ISO acumulada de 8247 sustituciones. El diagnóstico no añadió fuente española, así que no demuestra renderizado.

Evidencia A: SCRIPT.DAT conserva exactamente 633344 bytes, SCRIPT.TBL intacta, 1625 inicios de bloque fijos, 51705 comandos, 46308 no textuales byte-exact, 348 PSPFS ajenos idénticos, tres hermanos DSARC intactos, IMY roundtrip. PERO 2712 comandos cambian offsets dentro de 24 bloques (2221 no textuales y 491 textuales). La guarda de offsets fijos falla deliberadamente. No se ha probado el modelo MIPS de referencias ni PPSSPP; no es un parche seguro ni un release. Ver reports/R44_AUDITORIA.json.

Se añade una ruta independiente y explícita de compilación privada con el planificador completo (4899 SCRIPT +3348 otros +1 registro legítimamente inalterado). La ruta conservadora no cambia, y el exportador BPS rechaza este tipo de informe. La compilación acumulada y CI R44 deben validarse; no afirmar 100% funcional a partir de la prueba aislada.

```bash
python -m unittest discover -s tests -v
python tools/integrar_parche_seguro.py --iso /PRIVADO/USA.iso --candidate /PRIVADO/R44_LOCAL.iso --report /PRIVADO/R44_LOCAL.json --perfil-total-local-experimental --acepto-reubicacion-local
```

No distribuir ISO, BPS, recursos ni capturas comerciales. Oficial histórico 3724 intacto.
