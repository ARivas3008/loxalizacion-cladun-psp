# R45 — triaje de referencias locales (solo lectura)

ISO USA aportada por el usuario, extraída y autenticada por SHA-256. Se reprodujo de forma independiente la geometría R44 (33 residuales, exceso 40 B, 18 donantes, 2712 comandos movidos en 24 bloques). El núcleo scan se ejecutó con comandos de la ISO auténtica y 3 pruebas sintéticas. No se ejecutó el CLI del repositorio completo: checkout por red indisponible. El HEAD R44 tenía CI push 45656999910 y PR 45657016118 SUCCESS.

De 46308 comandos no textuales, ventanas deslizantes LE de 16/32 bits detectan 81 coincidencias locales de 16 bits, 0 absolutas de 16/32 bits y 0 locales de 32 bits hacia los offsets que se moverían. 79 fuentes, 11 destinos, 7 bloques; 77 posiciones pares de payload, 4 impares. Son coincidencias numéricas, NO punteros, NO ausencia demostrada de referencias indirectas. No se alteró la ROM ni se compiló la acumulada. Mantener guardas, perfil oficial y PR borrador.

Reproducción desde raíz del repositorio con ISO legítima privada:

    python -m tools.r45_referencias_locales --iso-original /PRIVADO/USA.iso
    python -m unittest discover -s tests -p 'test_r45_referencias_locales.py' -v

La salida incluye las parejas origen/destino para el trazado MIPS. Se necesita demostrar semántica de cada campo y ejecución A/B/A, o lograr los 33 textos sin cambios de offset. La cobertura conservadora de código (si se construye) permanece 8215/8248; el 100% R44 solo es planificación experimental.
