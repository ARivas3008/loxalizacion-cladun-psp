# Auditoría de los 2.803 candidatos anteriores

## Qué se investigó

Se volvió a abrir `DATABASE.DAT` desde la ISO original y se contrastaron las detecciones heurísticas con los **campos de longitud y desplazamiento identificados** de cada estructura. Se revisaron también nombres de archivo, falsos positivos y cadenas rasterizadas identificadas en seis PNG de `SYS.DAT2`.

## Hallazgos concretos

- **127 cadenas recuperadas** que no superaban el filtro textual antiguo (por ejemplo `Me?`, nombres con signos, valores como `HP-20%` y nombres en japonés).
- **133 correcciones** del texto o desplazamiento previamente asociado con una entrada.
- **56 valores de `LV.DAT`** eliminados por ser datos binarios interpretados como CP932.
- **32 coincidencias** eliminadas por estar fuera de campos textuales probados (fragmentos como `83A67>-.C5?B`, `Euﾛ"`).
- **64 referencias de archivo de mapas** (`rmap01.dat`, etc.) excluidas por ser referencias internas, no nombres de lugar para traducir.
- **391 registros vacíos** excluidos del corpus para traducción (su origen se mantiene en el historial de auditoría).
- **6 textos rasterizados** añadidos desde imágenes verificadas (dos `NO DATA` y cuatro `This is an RPG!`); las marcas comerciales no se traducen automáticamente.
- **809 registros de decisión** en `qa/decisiones_auditoria.csv`; 127 recuperaciones y 133 correcciones pueden coexistir con descartes.

## De qué se componen los 1.035 pendientes actuales

| Recurso | Cadenas | Motivo de prudencia |
| --- | ---: | --- |
| `DIFFICULTY.DAT` | 398 | Etiquetas de dificultad/advertencia, posiblemente de depuración, sin visualización comprobada. |
| `TIPATTR.DAT` | 302 | Nombres técnicos de atributos y terreno; **2 cadenas CP932 incompletas**. |
| `UP_MONSTER.DAT` | 156 | Nombres en campos textuales cuya exposición al jugador falta confirmar. |
| `EFFECT.DAT` | 70 | Etiquetas y descripciones breves de efecto; uso exacto por comprobar. |
| `MONSTER.DAT` | 69 | Campos japoneses de monstruos; falta determinar si tienen interfaz visible. |
| `DAIHYOU.DAT` | 14 | Nombres de personajes posiblemente auxiliares. |
| `SIEN.DAT` | 14 | Nombres de personajes posiblemente auxiliares. |
| `MAGIC.DAT` | 10 | Nombres o descripciones en japonés, sin prueba de visualización. |
| `CHAR.DAT` | 2 | Nombre y perfil de personaje en japonés, aparición sin comprobar. |
| **Total** | **1.035** | 1.033 de uso visual no demostrado + 2 con bytes incompletos. |

Los dos casos incompletos están en `TIPATTR.DAT`, índices 214 y 215, identificados como `CLD-F-TIPATTR-0214-nombre_atributo` y `CLD-F-TIPATTR-0215-nombre_atributo`. Conservamos bytes originales y el símbolo de sustitución `�`, en lugar de adivinar la terminación.

## Clasificación final

- **8.202 textos en formato reconocido**: incluidos diálogos, interfaz, créditos y gráficos. Son las mejores fuentes para traducir primero.
- **1.035 candidatos textuales estructuralmente delimitados**: incluidos en el corpus completo para no perder información, pero apartados para validación visual o reconstrucción.
- **No textuales**: excluidos del listado de traducción, con traza en `qa/decisiones_auditoria.csv`.

**Importante:** ninguna validación de campo sustituye una prueba de uso real en el juego. No es técnicamente correcto cerrar esos 1.035 como 'vistos en pantalla' sin PPSSPP, depuración de código o capturas de la edición.
