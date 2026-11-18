# Revisión contextual de enciclopedia y tutoriales — Cladun PSP

Fecha: 18/11/2026. Esta fase amplía la revisión lingüística; el corpus original de 9.237 entradas permanece intacto.

## Resultados

| Control | Valor |
|---|---:|
| Entradas originales / IDs alineados | 9.237 |
| Entradas con borrador español | 9.235 |
| Entradas sin borrador por fuente CP932 incompleta | 2 |
| Entradas posteditadas o normalizadas acumuladas por IA | **369** |
| Entradas automáticas sin revisión narrativa individual | **8.866** |
| Revisiones nuevas basadas en el contexto | **130** |
| Instancias duplicadas con terminología unificada | **66** |
| Nuevas modificaciones de texto en esta fase | **196** |
| Marcadores protegidos alterados | **0** |
| Alertas numéricas pendientes | 19 |
| Alertas de saltos de línea pendientes | 201 |
| Entradas con alertas de QA | 1.240 |

## Qué se revisó

Se leyó el segmento continuo de enciclopedia, carteles de rumores y tutoriales de combate, con atención a los grupos 000151–000430 y a repeticiones de idénticas líneas de origen. Los principales defectos detectados eran los de traducción por frases aisladas, que a veces invierte sujeto y predicado o traduce un fragmento como una oración independiente.

Ejemplos reales de corrección:

| ID | Automática anterior | Contextual revisada |
|---|---|---|
| 000155 | «Hiyokki caerá.» | «dejan caer los Hiyokki.» |
| 000179 | «SP Uso de la magia.» | «el consumo de SP de la magia.» |
| 000184 | «Puede que sí.» | «que tengan los enemigos.» |
| 000223 | «Celda Arcanus» | «Arcanus Cella» |
| 000232 | «Blindaje» | «Escudo» |
| 000256 | «Todos los equipos tienen título de propiedad.» | «Todo el equipo tiene títulos.» |
| 000320 | «que refuerza al personaje principal.» | «anima y fortalece al personaje principal.» |
| 000338 | «él/ella activó voluntad» | «que había activado» |
| 000350 | «reducción del tiempo de colada» | «y reducción del tiempo de lanzamiento.» |
| 000393 | «Nueva geoda» | «New-geon» |

Estos textos son **propuestas de post-edición por IA**. Deben probarse en el juego, con contexto de personaje, anchura de ventana y referencias cruzadas, antes de su aprobación humana.

Se normalizaron además otras apariciones con el mismo original inglés de las entradas revisadas; las 66 coincidencias se identifican en el registro de cambios.

## Trazabilidad

- [CSV bilingüe de trabajo](../traduccion/CLADUN_BORRADOR_ES.csv) con el original sin alteraciones y el estado de revisión.
- [Registro de los 196 cambios](../qa/revision_contextual_2026-11-18.csv) con texto anterior, propuesta y recurso.
- [Guion bilingüe](../traduccion/CLADUN_BORRADOR_BILINGUE_FAQ.txt) y [TXT español](../traduccion/CLADUN_BORRADOR_ES.txt).
- [Incidencias](../traduccion/INCIDENCIAS_QA.csv) y [resumen de QA](../reports/qa_traduccion_es.json).

## Pendiente

No se ha efectuado una corrección narrativa de las 8.866 entradas restantes. La revisión de estilo no demuestra compatibilidad con límites de bytes, marcadores gráficos o fuentes PSP. El prototipo de fuente [F5A0–F5B2](FUENTE_ES_PROTOTIPO.md) es otro trabajo, con prueba binaria pero sin validación visual en PPSSPP. **El proyecto aún no tiene una ISO española funcional**.
