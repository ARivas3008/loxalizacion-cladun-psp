# Historial de cambios

## 0.3.0 — 2026-11-17 — Auditoría estructural y enfoque en texto traducible

- El corpus público pasa a organizarse alrededor de `CLADUN_TODO_TEXTO_ORIGINAL.txt` y el CSV maestro, no de los opcodes/instrucciones del motor.
- Auditoría de campos en 20 tablas con estructura fija, tablas directas de nombres y `MAHO-JIN.DAT`.
- Recuperación de 127 cadenas omitidas; corrección de 133 fuentes/offsets.
- Exclusión documentada de 56 artefactos numéricos, 32 falsas cadenas y 64 referencias a archivos internos.
- Clasificación de 1.033 cadenas con uso visual por comprobar y 2 cadenas con bytes CP932 incompletos.
- Exportación de un TXT con 9.237 grupos numerados, originales sin traducir e IDs de procedencia.
- Actualización de documentación, normas, QA y pruebas reproducibles.

## 0.2.0 — 2026-11-17 — Primera extracción orientada a traducción

- Se retiraron de la presentación pública los índices de instrucciones del motor y se publicó el primer corpus de 9.212 candidatos, sujeto a revisión.

## 0.1.0 — 2026-11-17 — Inventario inicial

- Reconocimiento de contenedores de la edición USA PSP, scripts y tablas básicas. Los resultados iniciales no demostraban cobertura textual completa.
