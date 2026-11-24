# Cladun ES — R26: auditoría hacia ROMhacking 100 % sin falsificar ejecución

**Fecha:** 24 de noviembre de 2026. **Objetivo:** completar técnicamente las 8.248 sustituciones previstas en la ISO propia USA de Cladun. **Resultado del relevo:** comprobación auténtica A y planificador B de 8.248; herramienta para construir un único piloto ISO con las 8.248; **NO se ejecutó ese piloto completo contra PPSSPP ni se aprobó oficialmente el 100 %**.

## Referencia congelada y estadísticas por evidencia

Repositorio `ARivas3008/loxalizacion-cladun-psp`, rama `integracion-eventos-segura-20261120`, PR #7 OPEN/DRAFT base `revision-manual-dialogos`; no merge/force push, no ISO comercial publicada.

| Métrica | Verificado | Clase |
|---|---:|---|
| ISO USA original | 305.496.064 B, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f` | A |
| Índice de recursos PSPFS | 349 | A |
| `SCRIPT.DAT`, `SCRIPT.TBL` | 633.344 B / 52.016 B | A |
| Scripts / comandos / comandos no textuales | **1.625 / 51.705 / 46.308** | A |
| Comandos textuales, con / sin texto | **5.397 = 5.207 + 190** | A |
| Total de padding original de 1.625 scripts | **14.621 B** | A |
| Registros del corpus canónico | 9.237 | B |
| **Cambios reales de bytes que el planificador admite** | **8.248 = 4.900 SCRIPT + 3.348 otros** | B |
| Cambios SCRIPT de longitud variable / igual | 4.524 / 376 | B |
| Texto SCRIPT de ancho igual pero ya idéntico al inglés | 307 (no requiere cambio) | B |
| Cobertura oficial **ya validada** | **3.724 / 8.248 = 45,15 %** | histórico; sin nuevos C |
| R26 planificador completo (no aplicado/validado en juego) | 8.248 / 8.248 como objetivo **B** | B, **no C** |

SHA256 auténticos: `SCRIPT.DAT=c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`; `SCRIPT.TBL=f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. De los 5.207 textos de SCRIPT, **683** tienen el mismo tamaño que la fuente: 376 necesitan editar bytes y **307 son ya idénticos**, lo que explica la discrepancia inicial del prototipo. El planificador original no había perdido textos; el conteo anterior de 5.207 modificaciones de SCRIPT era incorrecto. CI rechazó primero ese supuesto, después se corrigió a **4.900+3.348** mediante evidencia real de GitHub Actions.

## Hallazgo A: por qué un reemplazo universal puede romper eventos aunque sobre espacio global

Se cruzaron los 5.207 textos canónicos por (archivo DSF, script ID) con los **1.625 registros auténticos de SCRIPT.TBL**, de los que 586 tienen textos que cambian. Tras verificar los 51.705 comandos:

1. Sin ligaduras: **2.883** textos traducidos crecen **17.108 B**; **1.641** se reducen **7.414 B**; **683** retienen longitud. El cambio neto es **+9.694 B**. Aunque la suma global de padding es 14.621 B, está distribuido entre bloques distintos: **253 bloques** necesitan más espacio que su padding. Suman **8.077 B** de déficit local; el peor bloque necesita **1.459 B**.
2. Usando las **44 ligaduras seguras** ya modeladas, aplicadas al máximo solo a las traducciones crecientes cuyo origen no contiene controles, sin insertar espacios al final de las traducciones más cortas: se puede ahorrar teóricamente **14.076 B** del crecimiento. El cambio neto pasa a **−4.382 B**. Aun así, **29 bloques** conservan déficit local (215 B total, máximo individual 34 B). **74 textos crecientes** tienen marcadores/orígenes que este método no considera seguros para ligaduras; **807** de los crecientes seguros aún exceden la longitud original por un total de 2.482 B.
3. La mejora **253→29** y **8.077→215 B** es un límite inferior teórico y una orientación para ingeniería inversa, no una ISO con el 100 % funcionando. Incluso un bloque que cabe en el mismo espacio podría tener comandos desplazados internamente: las referencias ocultas del motor PSP MIPS no han sido localizadas ni demostradas.
4. La ISO contiene un `PSP_GAME/SYSDIR/EBOOT.BIN` con cabecera **`7E505350` (~PSP)**, ejecutable PSP empaquetado/cifrado. Este relevo no descifró ni desensambló la lógica, y no inventa PCs MIPS ni referencias a offset. El modelo de eventos sigue incompleto y requiere pruebas C.

Herramienta **`tools/r26_script_full_capacity_audit.py`**: reproduce B sin ISO o audita A autenticada con `--iso-original`; verifica hashes, script ID, starts, la tabla, 51.705 comandos, padding, crecimiento y ambos escenarios; aborta si las cifras A/B reales se desvían. Tests **`tests/test_r26_script_full_capacity_audit.py`** cubren fuentes canónicas, cálculos, cambios de la tabla y errores negativos. Los resultados A se obtuvieron de la ISO privada real sin alterar su contenido.

## Piloto total R26: ingeniería implementada, no aprobado

**`tools/r26_piloto_total_8248_privado.py`** usa el integrador existente `tools/integrar_parche_seguro.py` y separa dos modos:

- Sin ISO: `preview()` autentica la identidad del corpus, llama al **planificador real** y exige **8.248 cambios** compuestos por **4.900** en SCRIPT (**4.524** con distinta longitud, **376** de igual longitud) y **3.348** en otros recursos. Conserva 307 textos de script que ya coinciden y no consumen cambios de bytes; devuelve solo métricas, no diálogos.
- Con ISO propia y opción de riesgo explícita `--i-accept-experimental-moving-event-offsets`: intenta producir **un único piloto privado y nuevo** con 8.248 cambios, ampliando SCRIPT.DAT, ajustando SCRIPT.TBL y colocando contenedores textuales al final de DATA.DAT cuando procede. Rechaza SHA incorrecta, objetivo preexistente, recuentos incorrectos, mutaciones de 46.308 instrucciones no textuales u orden de opcodes, y **exige informar que cambian offsets**. Si una guarda posterior falla, borra el archivo piloto. No publica ISO, BPS ni binarios.
- El integrador prueba aislamiento estático de los demás PSPFS, no de todas las dependencias de control del PSP MIPS. Este modo no usa las 44 ligaduras ni el rellenado con espacios; reescribe la longitud de los opcodes, con el riesgo explícito correspondiente. **No se ha ejecutado en este relevo el comando de creación de la ISO combinada completa** porque no hay checkout local íntegro del corpus traducido junto a la ISO en el contenedor, ni PPSSPP oficial 1.20.4 disponible. Tampoco existe autorización de liberar el parche.

Comandos de reproducción en un checkout privado:

```bash
python tools/r26_script_full_capacity_audit.py
python tools/r26_piloto_total_8248_privado.py
python -m unittest discover -s tests -p 'test_r26*' -v

# Únicamente con ISO adquirida legítimamente, fuera del repositorio:
python tools/r26_script_full_capacity_audit.py \
    --iso-original /PRIVADO/Cladun_USA.iso
python tools/r26_piloto_total_8248_privado.py \
    --iso-original /PRIVADO/Cladun_USA.iso \
    --candidate /PRIVADO/Cladun_R26_8248_SOLO_EXPERIMENTAL.iso \
    --i-accept-experimental-moving-event-offsets
```

**Importante:** no ejecutar la ISO experimental como parche público; su reconstrucción puede romper saltos de evento, lógica de escenas o referencias internas. Para aprobarla, primero registrar la trazabilidad MIPS/DSARC de todas las referencias, probar A/B/A en PPSSPP 1.20.4 y completar la QA Q071–Q075. Nunca alterar la ISO original ni subir contenido comercial.

## QA, CI y criterio de cierre

Se agregaron **Q071–Q075** a `qa/MATRIZ_BETATESTING_COBERTURA.csv` (75 casos definidos; los 5 nuevos siguen **NOT_RUN**): reinserción total privada, referencias MIPS, 29 bloques deficitarios, campaña visual A/B/A de 8.248, parcheador Win64/BPS. CI de GitHub ejecuta las pruebas B del planificador 8.248 y la reducción de déficit, y verifica que ninguna herramienta nueva declare 100 % oficial. Los informes y porcentajes oficiales se conservan hasta existir pruebas A/B/C y 0 errores P0/P1.

Cierre mínimo para marcar **romhacking 100 % real**: una misma ISO privada con 8.248 sustituciones autentificadas y recursos intactos; todos los saltos y dependencias MIPS verificados/ajustados; fuentes y caracteres correctos; PPSSPP oficial con capturas auténticas y recorrido completo; reversión A/B/A; 8.248 entradas auditadas editorialmente según contexto; BPS/EXE Windows E2E. Hasta entonces **3.724/8.248 (45,15 %)** siguen siendo la métrica verificada, y la capacidad teórica B no la reemplaza.

**Continuación recursiva:** `prompts/SIGUIENTE_TAREA.md` debe entregar R27 para construir y depurar la ISO piloto, resolver las 29 insuficiencias y las referencias MIPS, sin falsear C, manteniendo T/G/R/Q independientes.

### Auditor sin escritura de offsets de los 4.900 cambios

Se añadió `tools/r26_auditar_reubicacion_eventos_total.py`. El modo B ejecuta el planificador canónico y verifica exactamente **4.900** offsets textuales únicos (4.524 sustituciones que cambian de longitud, 376 del mismo tamaño; 307 textos ya idénticos) sin crear archivos del juego. El modo A toma la ISO propia USA auténtica, reconstruye `SCRIPT.DAT/TBL` **solo en memoria** mediante `text_command_rebuild`, reparsea 51.705 comandos con `script_event_guard.audit_script_rebuild` y produce contadores de offsets, starts, opcodes y comandos no textuales reubicados, hashes y metadatos **sin exportar ningún diálogo ni binario**. Rechaza cualquier mutación del orden de opcodes, IDs o bytes no textuales, y exige registrar que la reconstrucción desplaza comandos; aun así **no identifica ni corrige punteros MIPS**, y no es una ejecución C.

```bash
python tools/r26_auditar_reubicacion_eventos_total.py
python tools/r26_auditar_reubicacion_eventos_total.py \
    --iso-original /PRIVADO/Cladun_USA.iso
```

Se incluye `tests/test_r26_auditar_reubicacion_eventos_total.py`. Este relevo no ejecutó su modo A por carecer de checkout completo del corpus dentro del contenedor del binario original. Su resultado A queda pendiente sin estimar el número de instrucciones que realmente se moverían.
