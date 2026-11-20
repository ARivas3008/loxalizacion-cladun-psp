# Exportación de parches BPS experimentales

El proyecto puede generar una **ISO candidata privada** mediante `tools/integrar_parche_seguro.py`. Para distribuir cambios sin distribuir una ISO comercial, el siguiente componente genera un parche BPS1 que necesita la ISO original del usuario. **No se publica un parche final hasta validar el juego en PPSSPP.**

El generador `tools/generar_parche_bps.py` comprueba el SHA-256 de la ISO original (edición USA auditada), la correspondencia entre el informe del integrador y el SHA-256 de la candidata, que estén los 9.237 grupos previstos y que no hayan cambiado recursos PSPFS ajenos. Crea un diferencial con comandos estándar SourceRead y TargetRead, verifica los CRC32 del formato BPS y *aplica su propio parche a la ISO original en una carpeta temporal*. Publica el archivo BPS únicamente si la imagen reconstruida coincide por SHA-256 con la candidata.

## Flujo local, sin redistribuir ISO

~~~bash
python tools/integrar_parche_seguro.py \
  --iso Cladun-USA.iso \
  --candidate Cladun-ES-PRIVADA.iso \
  --report informe_integracion.json

python tools/generar_parche_bps.py \
  --original Cladun-USA.iso \
  --candidato Cladun-ES-PRIVADA.iso \
  --informe-integracion informe_integracion.json \
  --salida Cladun-ES-EXPERIMENTAL.bps \
  --informe-bps informe_bps.json \
  --experimental
~~~

La segunda orden requiere `--experimental` de forma explícita; no significa que la ISO funcione, ni que se haya ejecutado una prueba en PPSSPP. No crea ni publica assets comerciales por sí sola. Una vez validado el arranque, menú, guion, caracteres españoles, retratos, mapas y combate, debe habilitarse por separado el protocolo de publicación final.

Si falla el cotejo de hashes, la integridad de un recurso ajeno, el CRC del parche o el proceso de reconstrucción, la ejecución se rechaza. El parche BPS jamás sobrescribe el original ni una salida existente.
