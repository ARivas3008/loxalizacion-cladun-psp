# 05 — Limitaciones conocidas y trabajo verificable restante

1. **Contenido que aparece solo en imágenes:** se examinaron los seis PNG conocidos de `SYS.DAT2`. No se ha completado la inspección visual de `.MPB`, IMY u otros atlas/recursos que puedan contener palabras dibujadas.
2. **Cadenas de ejecutable:** todavía no se ha demostrado si todos los rótulos usados por EBOOT se extraen de los recursos conocidos.
3. **Etiquetas japonesas posiblemente internas:** 1.033 unidades tienen pendiente comprobar uso real en PPSSPP. No corresponde traducirlas automáticamente sin contexto.
4. **Caracteres truncados de origen:** dos campos CP932 incluyen bytes finales incompletos; el hexadecimal permite localizarlos, pero no recupera los caracteres perdidos.
5. **Rutas narrativas:** el orden del bloque/offset está conservado, pero no se ha validado la ejecución de todas las ramas del juego.
6. **Versión/edición:** la evidencia procede de una única ISO con hash identificado. No hay verificación cruzada con otras ediciones completas, demos, DLC u otras regiones.
7. **No hay inyector:** este proyecto es una fuente de textos e índices, no un parche funcional. No se han aplicado traducciones ni realizado pruebas de localización de español en consola.

**Criterio de cierre de cobertura:** revisión visual de todos los recursos relevantes, búsqueda de diferencias entre texto presentado en pantalla y corpus, validación de rutas y menús, pruebas de reinserción, y un registro explícito de textos descubiertos/descartados. Hasta entonces no afirmar «100 % de texto».
