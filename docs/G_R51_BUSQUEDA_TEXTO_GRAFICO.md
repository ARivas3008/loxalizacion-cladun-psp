# G-R51 — búsqueda visual de texto narrativo adicional

Se autenticó la ISO original (SHA en JSON) y el ZIP R50. CI R50 45695689646 SUCCESS. Se decodificaron 415 cargas (231 IDT, 24 LDT001, 57 LDT002, 39 MAPTIP, 37 MPB, 27 SYSGRA), y se abrieron nueve PNG originales. Cuatro cargas SYSGRA son tablas de paleta, seis atlas FONT no se reexaminaron. Total inventariado: 426 superficies. El recuento de cargas decodificadas no implica clasificación visual definitiva. Las 24 tiras LDT001 no se interpretan aún como texturas verificadas. IDT se revisó con el modelo primario; variantes ambiguas y CLUT externas quedan pendientes. Los 13 IDT 26–38 presentan un único índice bajo ese modelo.

Se reconstruyeron 37 mapas MPB; KYOTENBG y KYOTENBG_B requirieron longitud extendida de banderas (u16 cero + u32). Los mapas revisados contienen escenarios, fondos y rótulos. No se ha identificado otro párrafo narrativo además de IMY192 y su extracto en PIC0. Hallazgos adicionales:

- TRIAL_BG.MPB: anuncio japonés multilínea, con precios 5.229/4.000 yenes; comprobar accesibilidad USA antes de traducir.
- TITLE.MPB: título japonés y beta; verificar si es recurso residual.
- NIS_LOGO.MPB: texto inglés de presentación del editor.
- KENRI.IMY: aviso legal inglés, preservar nombres y copyright; valorar traducción de fórmula legal.
- SYS1.IMY: la versión española R50 conserva caracteres japoneses. Determinar función antes de editar.
- ANIME002.LDT 6990/0: pequeños rótulos japoneses, contexto pendiente.

Las previsualizaciones R50 de TUIKA_MES, DAMAGE, MAHO_ST, WINDOW01 y SYS1 se inspeccionaron; la narración de PIC0 coincide con las últimas tres líneas canónicas. No se observó otro relato en los atlas de animación y mapas revisados. La búsqueda es estática, no PPSSPP, y no certifica ausencia absoluta de texto oculto, fuentes ni recursos de formatos aún ambiguos. No se cambió ninguna imagen ni el texto canónico del usuario. PR sigue DRAFT.
