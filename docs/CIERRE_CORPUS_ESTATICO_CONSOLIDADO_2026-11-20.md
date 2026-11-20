# Cierre de la revisión estática consolidada — Cladun PSP (20/11/2026)

**Estado:** la revisión estructural de todas las entradas recuperadas y la
conciliación de cambios de esta fase están completadas. **No es una certificación
literaria humana línea por línea ni una aprobación del parche para jugar.**

## Cobertura e integridad

- **9.237 registros originales** conservados en el orden de extracción.
- **9.235 traducciones en el CSV** y dos excepciones acotadas: grupos
  `008723` y `008724`, cuyos campos japoneses ya están truncados en los
  bytes originales. Sus etiquetas españolas de inserción están declaradas en
  `tools/ajustes_campos_es.py`; no se inventan los caracteres perdidos.
- **914 intervenciones de la auditoría previa** (687 + 227), correspondientes
  a **910 registros distintos frente a main**. Se preservó toda esa rama
  mediante trabajo descendiente, no un reemplazo de su CSV.
- **226 nuevas correcciones, 226 aplicadas y cero pendientes en el plan**
  `qa/plan_revision_consolidada_2026-11-20.csv`.
- Las **110 alertas históricas** conservan su dictamen en
  `qa/AUDITORIA_110_ALERTAS_CERRADAS.csv`.
- Las **586 escenas** y los **2.216 cuadros de diálogo** siguen reconstruidos
  para cotejo contextual y reproducción de lecturas.
- La fuente canónica, sus bytes, IDs, offsets, localización y orden no se
  modificaron. El plan contiene preimagen, resultado y justificación por ID.
- Se regeneraron y publicaron los **TXT español, TXT bilingüe, lectura por
  hablantes, reconstrucción ES/EN y anexos**, junto con el registro de
  auditoría.

### Correcciones representativas

| Grupo | Problema detectado | Español corregido |
|---|---|---|
| 000793 | «Me pediste que te cuidara» atribuía a otra persona la petición de los padres | «me pidieron que te cuidara.» |
| 000799 | Frase inconexa tras «puedo hacer lo que quiera» | «durante los próximos seis meses.» |
| 000835 | Cambio erróneo de primera a tercera persona | «mientras busco un tesoro.» |
| 000922 | «Tengo... Despina» por «I-I am... Despina» | «Y-Yo soy... Despina.» |
| 001055 | Interrupción absurda de una frase sobre convertir a alguien en protagonista | «a cualquiera en personaje principal...» |
| 002763 | «Pasos de baile» para técnicas de combate | «nuevas técnicas» |
| 005687 | Menú de opciones saturado | «Vol. efectos» |
| 005712 | «Menos de 10 años» interpretaba una configuración numérica como una edad | «Menos de 10: SÍ» |
| 007522 | «Yingzhi no quiere» por etiqueta japonesa de atributo | «No requiere sabiduría» |
| 008325 | «discapacidad» en vez de «vida» en un texto japonés | «¡No me arrepiento de nada en mi vida!» |
| 009017 | Arma Claymore como «Casa antigua» | «Espadón» |
| 009025 | Nombre del arma Nemesis como «Justicia» | «Némesis» |

También se revisaron concordancias, signos, vocativos, nombres de armas,
monstruos, magia, opciones y rótulos. El término *Sub Character* queda
normalizado según el glosario como «personaje de apoyo» en los registros
corregidos. Los textos extensos de los campos fijos **no** se recortan en
el borrador literario: tres equivalentes adicionales de inserción fueron
definidos en `tools/ajustes_campos_es.py` bajo comprobación de capacidad.

## Verificación automatizada

La ejecución [44830171345](https://github.com/ARivas3008/loxalizacion-cladun-psp/actions/runs/44830171345)
terminó con éxito: **106 pruebas, 105 aprobadas y una omitida**,
incluyendo el plan reversible, términos, glifos, capacidad de campos,
guardas de recursos, script reconstruido e integridad del corpus.

El informe reproducible
`qa/INFORME_REVISION_CONSOLIDADA_2026-11-20.json` contiene los hashes SHA-256
del corpus original, traducción española y plan. El aplicador rechaza
cualquier preimagen alterada, marcador perdido, carácter no codificable,
cambio externo al campo español o aplicación parcial.

## Límites que siguen vigentes

La revisión integral **estructural** y la corrección focalizada de errores
demostrados no permiten afirmar que una persona haya leído con comprensión
dramática cada una de las **9.237 entradas** y todos los caminos narrativos.
Los textos con hablante no verificable siguen identificados como tales. Los
análisis automáticos no pueden garantizar por sí solos naturalidad perfecta,
condiciones de escena ni que todos los cuadros quepan en pantalla.

**Ningún BPS ni ejecutable se regeneró con este CSV.** La versión
experimental del parcheador v0.1.3 se publicó **antes** de estas 226
correcciones y no debe presentarse como portadora del corpus actual.
Tampoco se ha comprobado en PPSSPP que se pueda acceder al segundo nivel
o abrir la enciclopedia. Estos son fallos de ejecución y reinserción que
requieren diagnóstico funcional independiente.

**Criterio de cierre de esta fase:** cobertura de campos, alineación con
fuente original, plan de 226 cambios completamente aplicado, integridad,
codificación y pruebas automáticas, con dos excepciones japonesas explícitas.
**No** declarar «100 % calidad literaria certificada» ni «juego terminado».
