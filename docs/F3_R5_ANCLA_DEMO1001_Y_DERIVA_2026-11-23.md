# CLADUN ES — F3-R5: puente de procedencia ISO → 97 textos demo1001 y riesgo de desplazamiento (23/11/2026)

**F3 ABIERTA, F2 ABIERTA, F4–F6 pendientes.** No se ha modificado ISO, SCRIPT.DAT, SCRIPT.TBL, traducción ni recurso gráfico. No se ejecutó PPSSPP oficial 1.20.4 en este relevo. Conservar evidencia por categorías A/B/C y el bloqueo `--event-safe-only`.

## A. ISO ORIGINAL auténtica — huella criptográfica del texto y su orden

Se revalidó la ISO USA del usuario: **305.496.064 bytes**, SHA-256 **b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f**. Se abrió únicamente en memoria `DATA.DAT` → PSPFS 231 `SCRIPT.SDT` → `SCRIPT.DAT` (SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`) y `SCRIPT.TBL` (SHA `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`).

El extractor privado contabilizó **1.625 scripts / 51.705 comandos**. Los siete bloques `demo1001_00/01` suman **878 comandos** y **97 campos textuales no vacíos, 2.728 bytes originales**. Para cada campo, se construyó una huella SHA-256 sobre **offset de contenido + ID de script + índice de bloque + orden de comando + longitud + bytes originales** con prefijo de dominio `CLADUN:F3:DEMO1001:SOURCE_AND_ORDER:v2`. Resultado:

`b0d42d8cd871246addf08a54e02c2a84cda52cab39f5810ef5ba2d9173e3e34e`

El fichero público `reports/F3_DEMO1001_GEOMETRIA_ORIGINAL_2026-11-23.json` solo lleva **offsets, índices, longitudes y hashes**, NO textos ni comandos originales. `tools/f3_anclar_intro.py` puede verificar la misma geometría de nuevo contra la ISO **solo en privado**, aprovechando el parser canónico y la condición de SHA de origen exacto.

## B. Enlace con borrador español REAL y GitHub Actions

A diferencia de un cotejo puramente sintético, la nueva prueba de integración **sí leyó el CSV auténtico `traduccion/CLADUN_BORRADOR_ES.csv` de 3,9 MB** en GitHub Actions, verificando su SHA de blob Git `400a9c9ec06f7456b5ec6e11f7502d711b0a976e`, 9.237 registros, las 97 filas del prólogo, offsets/IDs/bytes/textos originales, el anclaje criptográfico completo y la codificación CP932 española A1–B3.

Resultado B validado en el commit `e0e47fa0e145732c83769af22c3a57e3fcc8eb4c`:
- **97/97** filas coinciden con la huella original. Español: 2.859 bytes; original: 2.728 bytes.
- **85** cadenas de longitud distinta (**BLOQUEADAS**), **11** del mismo tamaño son solo candidatas y **1** sin cambio.
- **14 tests sintéticos locales** pasaron sobre adaptadores privados; en CI se ejecutaron **676 tests Python** sobre los módulos reales, con resultado PASS y una nueva prueba de integración CSV real.
- GitHub Actions `push` [45253114057](https://github.com/ARivas3008/loxalizacion-cladun-psp/actions/runs/45253114057) y `pull_request` [45253129304](https://github.com/ARivas3008/loxalizacion-cladun-psp/actions/runs/45253129304), ambas **SUCCESS sobre el mismo commit**. Esto es QA de código, NO gameplay.

## NUEVA cuantificación: deriva de offsets si se concatenan textos sin reparar referencias

La CI calculó la posición hipotética de cada comando en su bloque al sustituir cada cadena por su español codificado, manteniendo el orden original e **ignorando padding, saltos MIPS y referencias**. No escribió ningún archivo del juego.

| ID script | Comandos originales | Variación neta de bytes de texto | Comandos cuyo offset inicial cambiaría |
| --- | ---: | ---: | ---: |
| 100000 | 5 | 0 | 0 |
| 100100 | 422 | −1 | 268 |
| 100190 | 27 | 0 | 0 |
| 100101 | 339 | +115 | 298 |
| 100191 | 28 | 0 | 0 |
| 100110 | 23 | +15 | 10 |
| 100120 | 34 | +2 | 12 |
| **Total** | **878** | **+131** | **588** |

**588 NO significa 588 saltos rotos ni 588 direcciones MIPS**: mide el número de comandos cuyo offset cambiaría en una reconstrucción lineal hipotética. Incluso con una variación neta de solo 131 bytes, hay desplazamientos internos. Se ignoran los espacios de relleno, las posiciones absolutas externas, los saltos internos, los estados del juego y la posible lógica de alineación. **Esta auditoría NO autoriza relocalización**, ni demuestra cómo la ejecuta el motor.

## Código, reproducciones y guardas

Archivos nuevos: `tools/f3_anclar_intro.py`, `tests/test_f3_anclar_intro.py`, `reports/F3_DEMO1001_GEOMETRIA_ORIGINAL_2026-11-23.json`, `reports/RESULTADO_F3_R5_ANCLA_Y_DERIVA_2026-11-23.json`. El workflow `.github/workflows/validacion-integracion-eventos.yml` ejecuta `python tools/f3_anclar_intro.py` con el borrador real, pero **sin ISO comercial**.

~~~bash
# Ejecución CI sin contenidos comerciales:
python tools/f3_anclar_intro.py
python -m unittest discover -s tests -p 'test_f3_anclar_intro.py' -v

# En equipo con copia de ISO privada: requiere CSV y geometría públicos;
# NO crea ISO ni cambia scripts. Reporte de métricas solo en ruta privada.
python tools/f3_anclar_intro.py --borrador-es traduccion/CLADUN_BORRADOR_ES.csv --geometria reports/F3_DEMO1001_GEOMETRIA_ORIGINAL_2026-11-23.json --iso-original /PRIVADO/Cladun_USA.iso --reporte-privado /PRIVADO/INTRO_ANCLA_R5_NUEVO.json

python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
(cd patcher && go test ./...)
~~~

No se publicaron cadenas del juego, IMY, EBOOT, ISO, BPS, PNG, GE ni RAM/VRAM. Los 4.524 textos SCRIPT.DAT de longitud cambiante siguen bloqueados, y F2 conserva el ensayo CLUT2 de 9.144 texeles con 3.506 en subregiones protegidas, el comparador X11 A/B y el más reciente control temporal **A/B/A** (no hay nuevos fotogramas PPSSPP).

## C. Estado runtime y siguientes acciones

No hubo PPSSPP nuevo porque el AppImage oficial 1.20.4 no pudo recuperarse en el entorno (fallo DNS en terminal y descarga alternativa fallida). No existen nuevas PC MIPS, MIPS interpreter traces, imágenes, GE, RAM/VRAM, ni demostración de fuente gráfica del prólogo o TUIKA en combate. EBOOT `~PSP` sigue cifrado y BOOT.BIN es cero en ISO; no se obtuvo intérprete descifrado.

**Siguiente experimento obligatorio:** autenticar emulador/ISO/PID/socket/FD e iniciar la escena `demo1001` REAL. Observar el intérprete MIPS y demostrar las referencias y saltos verdaderos antes de contemplar mover cualquiera de los 85 textos. En paralelo, correlacionar prólogo inglés con recursos por I/O→RAM→GE→VRAM auténtica; la firma IMY tipo02 y la sonda de nombre ANIME000 no bastan. Para F2, exigir A/B/A de combate/habilidad USA/sonda con control temporal y QA multicontesto de 19 glifos. PR #7 OPEN/DRAFT, rama base inmutable, sin force push ni merge. Continuar la regeneración recursiva del prompt hasta F2–F6 realmente concluidas.
