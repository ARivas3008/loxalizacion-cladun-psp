# Limitaciones conocidas y próximas fases

| Área | Estado | Condición para cerrar |
| --- | --- | --- |
| Diálogos y opciones en `SCRIPT.DAT` | Estructura extraída | Comparar escenas reales y variaciones de ruta con PPSSPP. |
| Mensajes HUD (`STRTBL.DAT`) | Tabla recuperada | Validar mostrados dinámicos y códigos de formato. |
| Nombres/descripciones de `DATABASE.DAT` | Campos reconstruidos | Validar los 1.035 casos de uso o bytes sin resolver. |
| Créditos | Texto no vacío recuperado | Verificar su render final y saltos de línea. |
| PNG de `SYS.DAT2` | 6 rótulos traducibles identificados | Editar gráficos y verificar resultado visual. |
| Gráficos comprimidos `.IMY/.MPB` | No auditados exhaustivamente | Revisar si contienen etiquetas/rótulos. |
| Cadenas del ejecutable | No acreditadas como texto de usuario | Revisión estática dirigida y pruebas en ejecución. |
| Cobertura del juego completo | **No demostrada** | Test de rutas, opciones, finales, DLC y todos los menús. |
| Traducción al español | 0 registros traducidos | Traducción, revisión lingüística y QA. |
| Reinserción | No implementada | Crear inyector y parche que funcione en PPSSPP sin distribuir contenido protegido. |

**Prioridad técnica:** primero resolver casos `revisar_visibilidad.csv` y recursos gráficos faltantes; después contrastar el corpus contra la edición en ejecución, traducir y probar. No presentar una estimación de porcentaje de completitud sin un inventario de pantallas y assets verificable.
