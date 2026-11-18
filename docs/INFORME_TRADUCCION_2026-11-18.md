# Cladun: This Is an RPG! (USA/PSP) — traducción y cotejo, 18/11/2026

## Resultado de la ejecución

El corpus original permanece intacto y se ha añadido un **borrador español separado** que conserva 9.237 IDs, orden, texto original, bytes, scripts y offsets. Un borrador automático **no significa traducción final ni parche jugable**.

| Indicador | Resultado |
|---|---:|
| Unidades cotejadas con original de GitHub | 9.237 |
| Unidades con traducción/borrador español | 9.235 |
| Unidades sin traducción por fuente CP932 incompleta | 2 |
| Unidades posteditadas o normalizadas contextualmente por IA | 67 |
| Borradores automáticos aún sin revisión narrativa individual | 9.168 |
| Diferencias restantes en tokens protegidos | 0 |
| Cifras o notaciones que requieren cotejo | 19 |
| Cambios en cantidad de saltos de línea | 202 |
| Unidades cuyo uso en juego o decodificación aún debe comprobarse | 1.035 |
| Entradas con alertas de QA registradas | 1.256 |

La post-edición parcial la realizó **GPT-6**; no sustituye una revisión humana especializada. Dos errores temporales de `GOOGLETRANSLATE` en nombres cortos se resolvieron conservando el nombre propio.

## Herramientas comparadas

| Tecnología | Ventaja para Cladun | Limitación | Uso en esta entrega |
|---|---|---|---|
| **DeepL API** | Glosarios y contexto para mantener términos y mejorar frases cortas; controles de estilo | Necesita suscripción/API y no estaba conectada | **Recomendada para una futura segunda pasada** |
| **Google Translate mediante Google Sheets** | Traduce inglés y japonés; integración real disponible, procesa segmentos vinculados a IDs | Fallos en frases partidas, nombres y caracteres de control | **Utilizada para las 9.237 posiciones** |
| **GPT-6 (ChatGPT)** | Contexto narrativo, decisiones de estilo y restauración de marcadores | No demuestra automáticamente perfección ni sustituye pruebas del juego | **67 entradas revisadas/normalizadas y QA** |
| **Hy-MT2** | Modelo multilingüe abierto que puede ejecutarse localmente | Requiere pesos y recursos; no se probó esta edición | **Alternativa para pruebas posteriores** |

Fuentes: [DeepL — personalización/glosarios](https://github.com/DeepL/api-docs/blob/main/docs/customize/overview.mdx), [Google Sheets — GOOGLETRANSLATE](https://support.google.com/docs/answer/3093331?hl=es), [Allcorrect — QA de localización de juegos](https://allcorrectgames.com/insights/the-quest-for-the-perfect-score/), [Hy-MT2](https://github.com/Tencent-Hunyuan/Hy-MT2).

**Conclusión práctica:** un motor de traducción acompañado de glosario, contexto y controles es preferible a traducir el TXT como un documento sin estructura. DeepL tiene funciones idóneas para la fase profesional; la herramienta *efectivamente utilizada aquí* ha sido Google Sheets, seguida de post-edición parcial contextual.

## Comparación con el trabajo anterior

- ISO examinada: SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- TXT maestro original (cotejado byte por byte): SHA-256 `83db60b80939d54548980e38a612ae9ae9605bf85f2feba7834d0e826425756f`.
- La extracción registra **9.237 posiciones**, como en GitHub. El cotejo no revela nuevas unidades confirmadas; eso **no demuestra** cobertura absoluta del juego.
- Se ha incorporado `corpus/LECTURA_ORIGINAL_ESTILO_FAQ.txt` como lectura original junto al corpus canónico.
- Los restos de otros recursos y gráficos no confirman nuevas cadenas con evidencia suficiente; queda auditoría in-game, imágenes, ejecutable y DLC externo.
- Los 1.035 casos de fuente pendiente siguen pendientes. Los dos casos incompletos pertenecen a `TIPATTR.DAT`.

## Seguridad, calidad y reinserción

- Todas las variables reconocidas (por ejemplo `%6d`, `%02d`, `%s`, `⑨`, `⑰`, `④`) se conservan en los valores españoles que no están vacíos. Los casos problemáticos se repararon y comprobaron.
- Hay **19 alertas de cifras** y **202 de saltos de línea**. Algunas son cambios lingüísticos aceptables; se deben cotejar antes de parchear. Hay advertencias de visibilidad y glosario adicional en `INCIDENCIAS_QA.csv`.
- El TXT presenta segmentos separados tal como los conoce el motor: la traducción automática puede perder la relación entre frases consecutivas. Las 9.168 no posteditadas requieren revisión de sentido, tono, personajes y consistencia terminológica.
- **Bloqueo técnico:** CP932 no representa directamente los signos y letras habituales del español (`ñ`, vocales acentuadas, `¿`, `¡`). Hacen falta cambios de codificación/fuentes, tablas y límites por campo, además de validación en PPSSPP.
- **Ninguna traducción está aprobada para reinserción** por el mero hecho de aparecer en el CSV. No hay ISO parcheada ni se distribuyen binarios del juego.

## Archivos

- `corpus/LECTURA_ORIGINAL_ESTILO_FAQ.txt`: lectura del texto original (trabajo anterior).
- `traduccion/CLADUN_BORRADOR_ES.txt`: texto español para lectura.
- `traduccion/CLADUN_BORRADOR_BILINGUE_FAQ.txt`: original y borrador para cotejo frase por frase.
- `traduccion/CLADUN_BORRADOR_ES.csv`: CSV de 9.237 grupos con fuente original, traducción y estados, sin modificar el corpus maestro.
- `traduccion/INCIDENCIAS_QA.csv`: alertas y problemas por ID.
- `traduccion/GLOSARIO_PROPUESTA.csv`: terminología provisional.
- `reports/qa_traduccion_es.json`: métricas.
- `tools/verificar_borrador_es.py`: controles estructurales reproducibles.

La hoja utilizada como motor auxiliar fue [Cladun PSP — borrador de traducción asistida](https://docs.google.com/spreadsheets/d/1KE3Ah68nb7qy9mrSy2nhFNQkVCOZ5TniOtO-M1STPSk/edit), pero **la versión trazable del proyecto es el CSV comprometido en GitHub**.

## Próxima fase

Post-editar por script (mantener continuidad entre líneas), aprobar el glosario, confirmar en PPSSPP el uso de cada campo, analizar la compatibilidad de fuente/codificación y desarrollar un reinserter con pruebas que respeten límites y punteros.
