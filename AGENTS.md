# AGENTS.md — reglas obligatorias para cualquier asistente o colaborador

## Objetivo

Trabajar **solo en textos para localizar de Cladun: This Is an RPG! (USA/PSP)**. Nunca confundir comandos/opcodes, nombres de archivos, offsets, texturas y datos numéricos con unidades traducibles. Las herramientas de extracción pueden analizar instrucciones internamente, pero el corpus público se centra en **texto y procedencia mínima verificable**.

## Fuentes canónicas

- `corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv`: único registro maestro que contiene el texto original.
- `corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt`: visualización de los mismos grupos, generada y sin traducción.
- `qa/decisiones_auditoria.csv`: decisiones justificadas sobre pendientes antiguos.
- `reports/resumen.json` y `reports/qa_integridad.json`: recuentos de extracción comprobables.
- `traduccion/CLADUN_BORRADOR_ES.csv`: traducción separada, nunca sobrescribir el original.
- `traduccion/GLOSARIO_CANONICO.csv`: glosario CSV vigente; `GLOSARIO_PROPUESTA.csv` es histórico.
- `reports/preinsercion_estatica_2026-11-18.json`: corte estático de riesgos, no aprobación de inserción.

Los subconjuntos `confirmados_formato` y `revisar_visibilidad` son vistas derivadas; no editar en paralelo.

## Nunca hacer

1. No traducir, abreviar, reordenar, fusionar ni eliminar texto fuente sin un registro de auditoría justificado.
2. No cambiar `grupo_id`, `text_id`, `origen`, `offset_hex`, `bytes_hex`, script o índice; no eliminar repeticiones.
3. No calificar el 100 % de texto recuperado hasta auditar recursos gráficos, ejecutable, DLC y verificación en PPSSPP.
4. No inventar caracteres corruptos, descripciones, nombres, espacios de interfaz ni traducciones.
5. No subir ISO, PBP, recursos gráficos, fuentes, música, ejecutables o paquetes del juego a GitHub.
6. No agregar listados de comandos del motor al corpus destinado a los traductores.

## En modificaciones futuras

- Distinguir **campo textual estructural**, **visibilidad en pantalla** y **facilidad de reinserción**: son pruebas diferentes.
- Separar los 1.035 pendientes; no presentarlos como ya comprobados visualmente.
- Conservar texto en inglés o japonés exactamente como sale de sus bytes.
- Escapar cuidadosamente variables `%s`, `%d`, `%02d`, secuencias y saltos de línea.
- Ejecutar `python -m unittest discover -s tests -v`, `python tools/verificar_integridad.py --raiz .`, `python tools/verificar_borrador_es.py` y `python tools/auditar_preinsercion_es.py`.
- Toda post-edición de `traduccion/CLADUN_BORRADOR_ES.csv` debe sincronizar el TXT español y el TXT bilingüe **en el mismo commit**, con registro CSV de antes/después.
- Diferenciar revisión textual por IA de revisión narrativa humana o renderizado probado; ninguna de las dos últimas está acreditada.
- Toda corrección de extracción debe actualizar el corpus maestro, TXT, subconjuntos, registro de auditoría y resumen **en el mismo commit**.
- En reportes distinguir siempre entre lo **verificado**, lo **probable** y lo **pendiente**.

## Blindaje obligatorio en reinserción

- **Nunca** desplazar bytes de otro recurso para hacer espacio a una traducción; rechazar operaciones que no quepan en los slots originales.
- Conservar y verificar cada entrada PSPFS y todos los miembros DSARC no intervenidos; cualquier diferencia de SHA-256 detiene la compilación.
- Los scripts, por ahora, solo admiten ensayos de cambio con igual longitud en bytes. No reconstruir punteros internos por suposición.
- No afirmar que CP932 privado F5A0–F5B2 sea representable visualmente sin haber instalado y probado sus glifos en FONT.ARC.
- No distribuir ISO, fuentes ni texturas comerciales. El ensayo temporal no demuestra funcionamiento en PPSSPP.
- Mantener `original`, `bytes_hex`, offsets e IDs sin modificaciones; el español vive en campos separados.

## Bloqueo de seguridad adicional

- La correspondencia PUA y los 19 glifos debe ser estrictamente `F5A0–F5B2`; no volver a introducir `F040–F052`, que desordenaría FONT.BIN si se insertara por código sin preservar índices.
- Todo cambio en la fuente requiere pasar `tools/font_es_guard.py` contra la ISO original.
- Cualquier cambio textual posterior se compara con su copia exacta de entrada mediante `tools/iso_guard_global.py`, con SHA-256 de origen, formatos invariantes y spans explícitos por miembro.
- Los veredictos `PASS_*_ISOLATION_ONLY` **no** certifican funcionamiento de PPSSPP ni muestran todos los textos; no permitir publicaciones de parche final sin esas pruebas.

## Umbral de inserción: fase 2026-11-18

- **4.576** scripts tienen traducciones de diferente longitud de bytes; **280** campos exceden el espacio; **816** carecen de modelo de capacidad. Estas entradas están bloqueadas, nunca recortar o mover otros recursos sin análisis de referencias.
- **3.557** entradas solo son candidatas a un ensayo estático. **0** entradas tienen aprobación de inserción final; evitar declarar «seguro», «completo» o «listo para parchear» basándose únicamente en el código.
- Los 19 nuevos glifos existen como **prototipo** (mapeo F5A0–F5B2). El texto localizado nunca debe publicarse ni mostrarse como funcional en PSP/PPSSPP sin prueba de render y carga.

## Contrato adicional: manifiesto enlazado a fuente

- Para una prueba textual binaria, generar primero el JSON con `tools/plan_textual_seguro.py` contra la ISO exacta de partida y los CSV actuales; no usar permisos manuales de spans.
- La guarda global exige `--manifest` y lo recalcula; cualquier byte distinto dentro o fuera de los tramos autorizados debe bloquear.
- El plan está limitado a SCRIPT.SDT/SCRIPT.DAT, igual longitud y estados de candidato estático. No da permiso para editar archivos gráficos, map tiles, retratos, fuentes o aumentar scripts.
- Mantener los avisos de PPSSPP: aislamiento binario no significa ejecución ni renderizado validados.

## Integración estructural experimental — 2026-11-18

- Congelar el texto del borrador salvo necesidad demostrada de compatibilidad; no alterar IDs ni fuente al implementar el empaquetado.
- El modo estricto de tools/integrar_parche_seguro.py debe detenerse cuando queden campos no insertables; no llamar al modo parcial «parche final».
- Se permite mover **únicamente las nuevas versiones de contenedores textuales a la zona añadida**, sin desplazar ni modificar bytes de recursos PSPFS ajenos, retratos, sprites, tiles ni sus offsets antiguos.
- Mantener el índice DSARC de otros miembros, los 349 registros PSPFS, todos los otros archivos ISO9660 y el códec IMY. El tamaño de ISO puede aumentar en sectores si los assets previos conservan sus posiciones.
- Rutas ahora modeladas: SCRIPT.DAT con longitudes y SCRIPT.TBL recalculados; campos DB de capacidad comprobada; STRTBL con punteros reconstruidos y reubicación interna aislada; STAFFROLL con EOL conservados.
- Las 280 entradas que desbordan campos fijos, 6 textos en imágenes y 2 fuentes incompletas están bloqueadas, no truncar ni escribir dentro de recursos ajenos. Añadir soluciones específicas y pruebas antes de desbloquear.
- La guarda estructural **no acredita** compatibilidad runtime con nuevos offsets PSPFS; no distribuir parche ni ISO experimental como versión jugable comprobada sin PPSSPP.
