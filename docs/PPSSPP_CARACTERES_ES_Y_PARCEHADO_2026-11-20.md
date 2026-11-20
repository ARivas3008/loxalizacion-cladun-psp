# Cladun ES v0.1.3: fuente de un byte y diferencial integrado

**Tipo:** ensayo reproducible con la ISO USA del usuario, no certificación
completa de jugabilidad. No publicar la ISO de origen ni la ISO candidata.

## Causa y reparación del espaciado

La versión v0.1.2 representaba `á`, `é`, `í`, `ó`, `ú`, `ñ`, `Ñ`,
`¿`, `¡` y los demás signos españoles mediante códigos privados de dos bytes
`0xF5A0...`, que el motor dibujaba con un avance inadecuado. La prueba en
PPSSPP mostraba `mú sica` y `configuració n` pese a que el CSV tenía palabras
correctas. La nueva versión inserta **19 códigos de un byte `0xA1..0xB3`**
y reordena la tabla ordenada de `FONT.BIN` y los seis atlas `IMY` para
conservar **pixel por pixel los 2.721 glifos originales**. Las grafías nuevas
no sobrescriben originales; el resto del contenedor se repaqueta con
comprobación de descompresión/recompresión.

## Ensayo real en PPSSPP

Con PPSSPP 1.20.4 Linux x86_64 se arrancaron la ISO con el códec antiguo y
la candidata con la nueva fuente. Se comparó la misma pantalla de selección de
música: la candidata antigua separaba `mú sica` y `configuració n`; la candidata
corregida imprimió `música` y `configuración` sin separación. Además se pasó
del menú al selector musical y a la introducción narrativa. No se verificó
la aventura íntegra, la creación de personajes, todos los diálogos, el
guardado/carga ni todas las configuraciones gráficas.

## Auditoría binaria

- SHA-256 original USA PSP: `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`
- SHA-256 ISO candidata experimental: `6d874a2e04fa9b27c14cbc42a49e91308d82c802b3f247ac1f0f1841953dd261`
- SHA-256 diferencial BPS: `300f0eabccf7bf64b2d1eb0e783d31a213f62fdc006ac193fad2918b23e92b80`
- 9.237 registros conservados; 8.250 sustituciones binarias y 987 equivalentes.
- 345 recursos PSPFS no relacionados: mismos offsets, metadatos y bytes.
- 2.721 glifos originales: las 6 páginas del atlas son idénticas por carácter
  en las nuevas posiciones de índice.
- Diferencial BPS reaplicado sobre la ISO original: reconstrucción SHA-256 exacta.
- El parcheador valida hash del ISO original, del BPS y del ISO resultado,
  y nunca sobrescribe la ISO fuente ni una salida existente.

## Riesgos y límites

Esta versión se distribuye como **experimental** para pruebas de una
copia privada de la ISO USA. Ni una auditoría estática ni una pantalla
correcta prueban cobertura visual del juego completo. Tampoco se ha
ejecutado manualmente la nueva GUI en una máquina Windows real; las
pruebas automáticas Windows comprueban compilación y motor BPS.

La fuente española permite comprobar y corregir ahora espacios/acento,
pero el ajuste fino de cuadros anchos o líneas largas sigue sujeto a
revisión contextual dentro del juego.
