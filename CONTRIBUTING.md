# Contribuir a la localización

## Alcance

Este repositorio concentra **texto del juego y herramientas para verificarlo**. No contiene una traducción española final ni admite cargas de copias del juego o recursos comerciales.

## Cambios de texto

- Trabaja sobre `corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv` como registro maestro. Para nuevas traducciones, solo edita la columna `espanol` (el corpus actual está íntegramente sin traducir).
- No alteres IDs, bytes originales, orden ni procedencia. No elimines duplicados.
- No cambies valores técnicos como `%s`, `%d`, saltos de línea y símbolos reservados.
- Cuando haya que corregir un campo fuente, documenta motivo, recurso, índice, offset y evidencia en el registro de auditoría. Regenera las vistas TXT/CSV en un commit conjunto.
- No declares un pendiente visual «confirmado» sin captura o verificación en PPSSPP con versión identificada.

## Comprobaciones antes de PR

```bash
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
```

## Propuesta de pull request

Describe el objetivo, archivo afectado, `text_id` o rango de grupos, evidencia de la corrección, consecuencias de variables/glifos y pruebas realizadas. Los textos originales deben poder reidentificarse en la misma ISO y no contener traducciones inventadas.
