# 01 — Alcance y criterios de clasificación

## Unidad de localización

**Una unidad = un campo textual original encontrado en el juego.** Una sola frase repetida diez veces en posiciones diferentes conserva diez unidades; ello permite reconstruir la correspondencia de claves/offsets al reinsertar. El conjunto contiene diálogos, opciones, nombres de interlocutores, interfaz, objetos, enemigos, lugares, habilidades, magia, atributos y créditos. Se añaden palabras rasterizadas en PNG **solo cuando fueron verificadas visualmente**.

## Estados

| `estado` | Significado | Acción correcta |
| --- | --- | --- |
| `pendiente_traduccion` | Texto recuperado de estructura reconocida o comprobado visualmente | Se puede planificar una traducción, pero falta QA de contexto y longitud |
| `requiere_comprobar_en_juego` | Campo con texto verdadero, pero posiblemente interno/de depuración | Cotejar capturas/rutas de juego; no dar por visible por su mera existencia |
| `requiere_reconstruccion` | Contenido parcialmente ilegible por bytes Shift-JIS/CP932 incompletos en la fuente | Documentar y cotejar; no completar con conjeturas |

`revision_fuente=verificado_formato` prueba que el extractor interpretó una estructura textual, **no** que se observó cada pantalla de ese guion. `revision_fuente=campo_binario_confirmado` prueba una posición fija válida de tabla, **no** necesariamente que se visualice en el juego. `revision_fuente=verificado_visual` se limita a los PNG examinados.

## Elementos excluidos de la lista para traducir

En `qa/decisiones_auditoria.csv` quedan registrados separadamente los nombres técnicos `rmap*.dat`, secuencias falsas procedentes de bytes numéricos, bytes fuera de los campos validados, líneas vacías y referencias decorativas. El logo **CLADUN** se registra como nombre comercial no traducible. Ninguna de estas exclusiones significa que su fila haya sido inventada o eliminada silenciosamente: se conoce su fuente o su razón de rechazo.

## Alcance del orden

El orden es el de lectura por recurso de la extracción, seguido por orden de registro/offset dentro de cada archivo. El orden de ejecución narrativo puede variar por ramas y eventos. `grupo_id` es secuencial de lectura; `text_id` identifica la procedencia técnica, por lo que pueden existir saltos en su secuencia. No renumerar IDs para cubrir saltos.
