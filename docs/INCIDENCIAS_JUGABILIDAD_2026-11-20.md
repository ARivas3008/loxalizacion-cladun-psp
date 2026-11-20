# Incidencias de jugabilidad y localización — 20/11/2026

**Edición auditada:** Cladun: This Is an RPG! (USA/PSP). ISO fuente SHA-256
`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.

**Evidencia:** seis capturas aportadas por el usuario (introducción, primera mazmorra,
menú de pausa y menú de opciones). Las imágenes son evidencia visual, **no**
pruebas de ejecución reproducible. No se incluyen fotos, ISO, BPS, fondos ni
otros recursos comerciales en el repositorio.

## Estado de incidencias

| ID | Incidencia | Hallazgo | Estado honesto |
| --- | --- | --- | --- |
| GAME-01 | No se puede subir al segundo nivel | El integrador reescribe longitudes textuales y cambia posiciones de instrucciones en SCRIPT.DAT. Reindexa los inicios de 1.625 scripts, pero **no está demostrado** que todas las referencias de control internas sigan siendo válidas. Es hipótesis, no causa confirmada. | **ABIERTO — bloqueo funcional, pendiente de A/B en PPSSPP** |
| GAME-02 | La enciclopedia no abre / no deja acceder | El ítem **Encyclopedia** existe en STRTBL original (posición 38). La captura muestra su etiqueta, pero no permite diagnosticar una falta de respuesta. Aislar SCRIPT.SDT frente a DATABASE.DAT sin cambiar recursos ajenos. | **ABIERTO — bloqueo funcional, pendiente de A/B en PPSSPP** |
| UI-01 | Menú de opciones saturado | STRTBL posiciones 479–510 contenía traducciones extensas de nombres cortos. 7 rótulos de selección pasan a etiquetas de máximo 18 caracteres; se ajustan los textos explicativos. | **CORREGIDO EN CORPUS; prueba de render pendiente** |
| LANG-01 | Frases fragmentadas y errores de traducción | Se cotejó `demo1001_00.dsf` con el original: “Your mom and dad / asked me to look after you.” estaba mal concordado; seis pasajes relacionados quedaron sin enlace gramatical. | **CORREGIDO EN CORPUS; prueba narrativa dentro del juego pendiente** |
| LANG-02 | Menú “Menos de 10 años” | Error de traducción de “Under 10 ON”; se reemplazó por “Menos de 10: SÍ”. | **CORREGIDO EN CORPUS; render pendiente** |

**Cambios hechos:** 24 unidades de `traduccion/CLADUN_BORRADOR_ES.csv` sincronizadas
con los dos TXT derivados, sin reescribir el original, `bytes_hex`,
`offset_hex` ni IDs. Registro individual:
[`qa/revision_capturas_2026-11-20.csv`](../qa/revision_capturas_2026-11-20.csv).
Pruebas: `tests/test_regresion_capturas_20261120.py`.

## Prueba A/B reproducible para aislar los dos bloqueos

Generar localmente, **sin sobrescribir la ISO original**, tres candidatas
independientes a partir del mismo original y la misma rama:

```sh
# A = traducción total (control experimental, NO versión estable)
python tools/integrar_parche_seguro.py --iso ORIGINAL.iso --candidate A-COMPLETA.iso --report A.json

# B = todo salvo SCRIPT.SDT (script original en inglés)
python tools/integrar_parche_seguro.py --iso ORIGINAL.iso --candidate B-SIN-SCRIPTS.iso --report B.json --experimental-parcial --excluir-recurso SCRIPT.SDT

# C = todo salvo DATABASE.DAT (menús/base de datos originales)
python tools/integrar_parche_seguro.py --iso ORIGINAL.iso --candidate C-SIN-DATABASE.iso --report C.json --experimental-parcial --excluir-recurso DATABASE.DAT
```

La opción `--excluir-recurso` exige `--experimental-parcial`; cuenta las
entradas omitidas en el informe y fuerza `todos_los_textos_insertados=false`.
No debe publicarse B ni C como parches terminados.

Para cada candidata: comenzar una partida nueva en **la misma versión de
PPSSPP**, entrar en el primer nivel, intentar avanzar al segundo, abrir la
enciclopedia desde el menú, abrir/cerrar opciones y alternar controles;
registrar fecha, versión de PPSSPP, backend gráfico, momento del fallo, log
y captura. Comparar también la ISO **sin modificar** como control D. Aun
si B funciona, no concluir que la causa es un salto antes de comprobar el
intérprete. Si falla también D, investigar requisitos de progresión,
guardado o comportamiento original.

| Prueba funcional | D ISO original | A completa | B sin scripts | C sin base de datos |
| --- | --- | --- | --- | --- |
| Subir al segundo nivel | Pendiente | Reportado fallo; no reproducido en este entorno | Pendiente | Pendiente |
| Abrir enciclopedia | Pendiente | Reportado fallo; no reproducido en este entorno | Pendiente | Pendiente |
| Opciones sin recortes | Original inglés | Pendiente | Pendiente | Original inglés |
| Diálogos y tildes | Original inglés | Pendiente | Scripts originales | Pendiente |

## Criterios para cerrar GAME-01 y GAME-02

1. Reproducir el fallo con una captura o save state identificable en la versión
   A y contrastarlo con la ISO original en el mismo emulador.
2. Determinar cuál de los recursos ocasiona el cambio mediante las variantes
   B/C y, si hace falta, aislamiento por script/entrada.
3. Reparar el mecanismo exacto (referencias, orden, control, formato o
   requisito de juego), sin modificar assets no textuales.
4. Pasar guardas ISO/PSPFS/DSARC, pruebas de regresión y validación real
   de segundo nivel, enciclopedia y regreso al menú.
5. Solo entonces reconstruir BPS, hashes y EXE. La versión privada v0.1.2
   **no incorpora estas 24 correcciones** y no se debe reetiquetar como nueva
   versión arreglada.

**Seguridad:** no subir ISOs, BPS que distribuyan datos comerciales, capturas
de recursos extraídos ni fuentes del juego. Los A/B son experimentales y
privados; el integrador sigue preservando la copia original.
