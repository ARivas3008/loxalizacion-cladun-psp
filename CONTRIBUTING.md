# Colaborar en la localización

El corpus está en fase de **catalogación y verificación**. Por ahora no se solicita que se traduzcan líneas; primero deben identificarse las cadenas y conservarse su posición exacta.

Las aportaciones de extracción deben incluir el recurso de origen, desplazamiento, bytes originales, justificación de que el campo es textual y comprobación de su uso en pantalla si se afirma que es visible.

Las futuras propuestas de traducción deberán editar solo `espanol` del CSV maestro; no renumerar `grupo_id`, no modificar `text_id`, no eliminar cadenas repetidas, y conservar marcadores `%s`/`%d`/`%02d`, saltos, glifos y variables. Los cambios deben pasar las pruebas de QA. Los textos marcados `requiere_comprobar_en_juego` y `requiere_reconstruccion` exigen evidencia antes de aprobarse.

No adjuntar copias de ISO, binarios de la PSP, gráficos, fuentes ni audio del juego en incidencias o solicitudes de cambio. El repositorio no distribuye un parche, y el contenido del videojuego mantiene sus derechos originales.
