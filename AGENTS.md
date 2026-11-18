# AGENTS.md — reglas obligatorias para cualquier asistente o colaborador

## Objetivo

Trabajar **solo en textos para localizar de Cladun: This Is an RPG! (USA/PSP)**. Nunca confundir comandos/opcodes, nombres de archivos, offsets, texturas y datos numéricos con unidades traducibles. Las herramientas de extracción pueden analizar instrucciones internamente, pero el corpus público se centra en **texto y procedencia mínima verificable**.

## Fuentes canónicas

- `corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv`: único registro maestro que contiene el texto original.
- `corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt`: visualización de los mismos grupos, generada y sin traducción.
- `qa/decisiones_auditoria.csv`: decisiones justificadas sobre pendientes antiguos.
- `reports/resumen.json` y `reports/qa_integridad.json`: recuentos comprobables.

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
- Ejecutar `python -m unittest discover -s tests -v` y `python tools/verificar_integridad.py --raiz .`.
- Toda corrección de extracción debe actualizar el corpus maestro, TXT, subconjuntos, registro de auditoría y resumen **en el mismo commit**.
- En reportes distinguir siempre entre lo **verificado**, lo **probable** y lo **pendiente**.

## Blindaje obligatorio en reinserción

- **Nunca** desplazar bytes de otro recurso para hacer espacio a una traducción; rechazar operaciones que no quepan en los slots originales.
- Conservar y verificar cada entrada PSPFS y todos los miembros DSARC no intervenidos; cualquier diferencia de SHA-256 detiene la compilación.
- Los scripts, por ahora, solo admiten ensayos de cambio con igual longitud en bytes. No reconstruir punteros internos por suposición.
- No afirmar que CP932 privado F040–F052 sea representable visualmente sin haber instalado y probado sus glifos en FONT.ARC.
- No distribuir ISO, fuentes ni texturas comerciales. El ensayo temporal no demuestra funcionamiento en PPSSPP.
- Mantener `original`, `bytes_hex`, offsets e IDs sin modificaciones; el español vive en campos separados.
