# R46 — verificación independiente del 0,40% residual

CI R45 push 45658190563 y PR 45658209284 SUCCESS. Con ISO USA privada auténtica se reprodujeron en memoria las 27 sustituciones anteriores y luego las 78 del diagnóstico R44 (33 residuales, 18 donantes, 27 anteriores). Los dos hashes SCRIPT.DAT coinciden exactamente con R43 y R44. Comprobación independiente de orden, opcode, ID, bytes no textuales, 1625 inicios y tabla intacta.

Se examinó cada uno de los 33 slots: todos crecen, ninguno es el último comando de su bloque; por tanto 0/33 pueden ampliarse conservando todos los offsets con la codificación actual. Dos desbordan incluso el padding final del bloque cuando se consideran individualmente. La combinación con donantes mantiene la tabla pero desplaza 2712 comandos, incluidos 2221 no textuales. No se ha validado la semántica MIPS. No se modifica el perfil oficial ni el conservador. No se fabricó una ISO acumulada ni se ejecutó PPSSPP.

El informe corresponde al replay independiente ejecutado localmente; la nueva CLI del repositorio proporciona una segunda implementación reproducible, no ejecutada localmente por falta de checkout. Ejecutar desde la raíz: python -m tools.r46_verificar_residuales --iso-original /PRIVADO/USA.iso. No distribuir recursos comerciales.
