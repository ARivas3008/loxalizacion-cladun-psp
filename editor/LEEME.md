# Editor de Cladun sin instalación

Abre `Cladun_Editor_Offline.html` haciendo doble clic. No se necesita instalar Python ni dependencias: el editor funciona en el navegador de forma local y no envía datos a ningún servidor.

Pulsa **Cargar CSV**, selecciona `traduccion/CLADUN_BORRADOR_ES.csv`, busca por ID (p. ej. `CLD-000803`), por inglés o por español, edita el campo **Español**, pulsa **Guardar cambio en memoria** y finalmente **Exportar CSV corregido**.

**Muy importante:** exportar no escribe nada en la ISO y no actualiza los archivos del repositorio automáticamente. Para validar y sincronizar el CSV corregido consulta la [guía](../docs/GUIA_EDICION_MANUAL.md) y ejecuta `tools/aplicar_correcciones_editor.py` desde la raíz del repositorio. Si un carácter no es insertable con el códec experimental o se altera un marcador del juego, la importación se rechaza.

Los nombres de hablante se basan en `personaje_interlocutor` / `0x6E` y continuidad corta; no son una garantía de atribución narrativa. Donde no se puede establecer con certeza aparecerá *Hablante no verificado*.
