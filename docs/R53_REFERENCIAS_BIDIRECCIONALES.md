# R53 — inventario estático bidireccional de la reubicación R52

ISO privada USA autenticada (SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f). Un parser independiente local reprodujo 51.705 comandos, 46.308 no textuales, 68 slots con delta, balance cero por bloque, 146 comandos movidos (104 no textuales) en 24 bloques. Los cuatro recuentos absolutos/locales LE16/32 son cero.

Se amplió el barrido a referencias relativas firmadas desde principio y fin del comando. Solo se conservan coincidencias en el mismo bloque con deriva distinta entre origen y destino. Resultado auténtico: 31 coincidencias numéricas, 22 con destino movido y 9 con origen movido y destino fijo; 27 fuentes, 21 destinos, 9 bloques, 12 opcodes. Una pareja tiene ambos extremos desplazados con deriva diferente. Todas son LE16. Frecuencias globales del mismo campo/valor permiten priorizar sin afirmar semántica. No son 31 saltos demostrados.

No se construyó ISO acumulada ni se ejecutó PPSSPP; Git directo no resuelve DNS, emulador no disponible. El código del repo se añadió para CI y reproducción posterior; la ejecución local fue independiente. No modificar R52, no promocionar porcentaje oficial, no publicar activos comerciales.

    python -m tools.r53_relative_bidir --iso-original /PRIVADO/USA.iso > /PRIVADO/r53.json
    python -m unittest discover -s tests -p 'test_r53_relative_bidir.py' -v

El informe genera exclusivamente metadatos; no exporta payload ni textos. Validación C pendiente de 146/146, incluida semántica de los 31 candidatos. La CI del HEAD R52 fue SUCCESS (push 45706285256 y PR 45706294187).
