# Cladun PSP — cierre de auditoría lingüística estática y decisiones de las 110 alertas

**Rama:** `revision-manual-dialogos` · **No es un parche nuevo ni una certificación de juego probado.**

## Qué se hizo

- Conservamos los **9.237 registros**, el inglés/japonés original, las rutas de origen, los desplazamientos y los datos binarios.
- Los **687 cambios previos** permanecen; se agregan **227 correcciones contextuales nuevas**, exclusivamente en `espanol`, con libro de antes/después y preimagen exacta.
- Se reconstruyeron otra vez **586 escenas** y **2.216 cuadros de diálogo**; el texto fuente de **5.207 fragmentos de script** y **4.030 registros de otros recursos** sigue identificado y ordenado.
- Cada una de las **110 alertas** anteriores recibió un dictamen individual en `qa/AUDITORIA_110_ALERTAS_CERRADAS.csv`:
  - 82 entradas de nombres propios de listas de jefes/personajes restituidas al nombre original;
  - 23 avisos de puntuación resegmentada considerados falsos positivos tras comparar la intervención completa;
  - 1 falso positivo de puntos suspensivos;
  - 1 unión de cajas descartada: existe una instrucción intermedia, no debe ensamblarse a ciegas;
  - 1 intervención corregida y recompuesta;
  - 2 nombres japoneses truncados que **no se pueden recuperar literalmente**; tienen sustitutos **«Aceite animado» y «Agua animada»** suministrados por `tools/ajustes_campos_es.py`, cotejados contra el campo real y su longitud.

## Errores sistemáticos adicionales encontrados fuera de las 110 alertas

La revisión del guion y de los nombres en `CHAR.DAT` y los opcodes `0x6E` permitió detectar que **Sunday**, **Sherbet**, **Coco**, **Bob**, **Asagi** y otros nombres seguían traduciéndose como días, postres, palabras corrientes o expresiones extrañas. También se corrigió el uso de «Mascarilla» donde el contexto trata sobre **la máscara** de la historia; los imperativos «¡Esperar!»; y descripciones de clase que hablaban absurdamente de «suscripciones» o «lanzadores abridores».

Todas las modificaciones se encuentran en `qa/plan_cierre_linguistico.txt` (formato CSV con extensión `.txt` para conservarlo como texto literal) y en la bitácora actualizada `qa/correcciones_manuales.csv`.

## Criterios de aprobación y excepciones

1. **Sí está completado:** cotejo estructural de los 9.237 IDs y su procedencia; normalización editorial focalizada; revisión y dictamen de las 110 alertas; reconstitución de todas las escenas con sus límites de cajas; pruebas automatizadas de integridad, marcadores, codificación y planes de integración.
2. **No está probado:** una lectura narrativa humana minuciosa de todos los 2.216 cuadros, línea por línea, en cada situación jugable. La reconstrucción es un control estático y no demuestra que se hayan revisado todos los matices de personalidad y tono. No presentar como «100 % de calidad narrativa certificada».
3. **Dos fuentes truncadas:** el borrador conserva intencionadamente su español vacío porque `tools/ajustes_campos_es.py` verifica bytes e inserta etiquetas cortas; el japonés original completo no es recuperable del campo cortado. Es una excepción de origen documentada, no un error de traducción oculto.
4. **PENDIENTES expresamente excluidos del alcance:** compatibilidad de acentos, espacios, glifos y saltos en PPSSPP; y generación/publicación de un `.exe` nuevo con estas revisiones.

Las 25 alertas de puntuación/segmentación aún aparecen en el **detector heurístico bruto**, por diseño, pero tienen veredicto editorial explícito: no se borran ni se maquilla la métrica de detección. Las dos cadenas incompletas se muestran igualmente como excepciones, no como texto original recuperado.

## Reproducibilidad

```bash
python tools/cerrar_qa_linguistico.py
python tools/cerrar_qa_linguistico.py --aplicar
python -m unittest discover -s tests -v
python tools/verificar_borrador_es.py
python tools/verificar_integridad.py --raiz .
```

El primer comando solo valida. El segundo solo escribe traducción y vistas después de comprobar el texto anterior exacto. Nunca sobrescribe ISO, retratos, tiles, música, fuente ni binarios.
