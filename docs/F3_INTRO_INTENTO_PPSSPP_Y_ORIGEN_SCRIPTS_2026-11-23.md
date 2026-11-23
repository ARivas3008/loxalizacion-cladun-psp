# F3 — Introducción en inglés: origen y traducciones identificadas en la ISO original (23/11/2026)

**F3 INICIADA, NO CERRADA. F2 SIGUE ABIERTA.** Se ha aceptado la prioridad solicitada: estudiar y preparar la introducción sin esperar a cerrar todo F2. Los resultados nuevos son de bytes auténticos de la ISO y del borrador español real en GitHub; **ninguna captura nueva de PPSSPP fue ejecutada en este entorno**.

## 1. PPSSPP oficial 1.20.4: evidencia histórica sí; ejecución nueva no

El usuario confirma la misma configuración anteriormente utilizada en F1: AppImage oficial `PPSSPP-v1.20.4-anylinux-x86_64.AppImage`, Linux x86_64, renderer llvmpipe, Xvfb 1280×720 y ventana 960×544. La documentación histórica `docs/RESULTADO_F1_PPSSPP_2026-11-21.md` confirma una ejecución real de esa versión y pruebas visuales de Opciones en aquel entorno. **No negamos ni invalidamos esa evidencia histórica**.

Al intentar usarla de nuevo hoy, el AppImage NO está en /usr,/opt,/tmp ni /mnt/data, tampoco PPSSPPSDL/PPSSPPQt. La URL oficial del release publicada en GitHub existe (el asset x86_64 ocupa **50.689.748 bytes**), pero `curl` falla con `Could not resolve host: github.com`; la descarga directa de herramientas también falló. Xvfb sí está instalado, pero no sustituye al ejecutable PPSSPP. Esto es un límite **del entorno actual** y no contradice la sesión F1 precedente. AppImage SHA-256 histórico:
`661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.

## 2. La causa de la introducción inglesa ya no es una sospecha general

ISO auténtica aportada por el usuario: **305.496.064 bytes**, SHA-256:
`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.

Se auditó la tabla ISO9660 real: 16 entradas en total; no existe un archivo llamado *.PMF en la raíz o subdirectorios ISO9660. Se inspeccionó además la tabla interna PSPFS de **349 entradas** y allí tampoco hay un nombre terminado en *.PMF. **Esto NO demuestra que no existan otras cinemáticas o texto incrustado en gráficos**, ni una reproducción runtime de una escena específica.

Los diálogos iniciales identificables se encuentran **en el contenedor script**:

- ISO9660 `PSP_GAME/USRDIR/DATA.DAT` → PSPFS índice **231** `SCRIPT.SDT` → DSARC `SCRIPT.DAT` + `SCRIPT.TBL`.
- `SCRIPT.DAT` original extraído SHA-256: `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`.
- `SCRIPT.TBL` original SHA-256: `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`.
- Entradas del comienzo de la narrativa: `demo1001_00.dsf` y `demo1001_01.dsf`. No confundir estos **nombres de script** con una prueba de que PPSSPP haya reproducido exactamente un bloque.

| Script ID | Nombre | Comandos auténticos | Campos originales no vacíos |
|---|---|---:|---:|
| 100000 | demo1001_00.dsf | 5 | 0 |
| 100100 | demo1001_00.dsf | 422 | 44 |
| 100190 | demo1001_00.dsf | 27 | 0 |
| 100101 | demo1001_01.dsf | 339 | 45 |
| 100191 | demo1001_01.dsf | 28 | 0 |
| 100110 | demo1001_01.dsf | 23 | 5 |
| 100120 | demo1001_01.dsf | 34 | 3 |
| **Total** | **7 bloques** | **878** | **97** |

Se contaron **98 opcodes textuales** (0x66, 0x69, 0x6E), uno con cadena vacía; los **97 no vacíos** suman 2.728 bytes de texto original. Estas cifras proceden de la ISO auténtica. El primer bloque con frases es 100100, y el siguiente es 100101. Se evita reproducir todo el texto del juego en el informe público.

## 3. Traducción española ya hecha: el problema es su **inserción segura**

El blob existente en GitHub `traduccion/CLADUN_BORRADOR_ES.csv` (SHA Git `400a9c9ec06f7456b5ec6e11f7502d711b0a976e`) mantiene **9.237 registros**. Se revisaron sus **97 filas** correspondientes a los dos scripts anteriores: las 97 tienen campo de traducción española. Se evaluó la longitud binaria con el **codec vigente** `tools/charset_es.py`, usando los 19 caracteres especiales A1–B3 y las codificaciones CP932 originales de símbolos ㊦, ㊧ y ㈱ (dos bytes cada uno).

| Script ID | Filas con español | Diferente longitud (aplazadas) | Longitud igual cambiada | Idénticas |
|---|---:|---:|---:|---:|
| 100100 | 44 | 38 | 5 | 1 |
| 100101 | 45 | 40 | 5 | 0 |
| 100110 | 5 | 4 | 1 | 0 |
| 100120 | 3 | 3 | 0 | 0 |
| **Total** | **97** | **85** | **11** | **1** |

Texto fuente de estos registros: **2.728 bytes**; español CP932 A1–B3: **2.859 bytes**. La variación total neta (+131 bytes) NO indica cuántos bytes deben desplazarse ni autoriza editar: **85 campos requieren cambiar el tamaño de su instrucción**. El modo `--event-safe-only` debe impedir esos 85 cambios hasta que exista un modelo demostrable de offsets, saltos, referencias externas y QA de ejecución. **Los 11 de longitud igual son solo candidatos**, no prueba de que se visualicen bien o ya se hayan integrado en la ISO F1. Solo uno permanece binariamente idéntico.

La clasificación del borrador y el inventario ISO se obtuvieron de fuentes auténticas por separado; la nueva herramienta integrada debe cotejar individualmente los 97 offsets y sus bytes para respaldar una afirmación conjunta. No se añadió ninguna traducción ni cambiaron los scripts.

## 4. Herramienta nueva, de solo lectura y fail-closed

`tools/f3_auditar_intro.py` valida SHA/tamaño exactos de ISO, lee ISO9660→PSPFS→DSARC sin modificar binarios, comprueba los 7 bloques (IDs y nombre), **878 comandos**, **98 opcodes de texto y 97 campos no vacíos**. Después valida que el CSV tenga 9.237 filas, 97 IDs de intro y una correspondencia 1:1 entre `offset_hex`, `bytes_hex`, `script_id`, nombre de script, longitud e ISO original. Codifica español con el codec canónico y rechaza cualquier discrepancia de cobertura o clasificación, sin reemplazar ni un byte.

Comando con una ISO que el usuario posee y resultado **privado nuevo fuera de Git**:

```bash
python tools/f3_auditar_intro.py \
  --iso-usa /PRIVATE/USA_original.iso \
  --borrador-es traduccion/CLADUN_BORRADOR_ES.csv \
  --reporte-privado /PRIVATE/F3_intro_comparacion_NUEVA.json
```

Para inspeccionar solo la estructura ISO sin el CSV, omitir `--borrador-es`; el informe marca la comparación con el borrador como NO ejecutada. Tests unitarios nuevos: `tests/test_f3_auditar_intro.py` (sintéticos, ver CI).

Un informe privado independiente de bytes originales fue generado: `F3_INTRO_BYTES_ISO_ORIGINAL_PRIVADO_20261123.json`, SHA256 `5f9865e5932c871b3e7b1a93b46e439fdb1979fd63041bccf404ed638c3bc5a0`. El informe público contiene SOLO métricas, ubicaciones y hashes: `reports/RESULTADO_F3_INTRO_ORIGEN_2026-11-23.json`.

## 5. Estado y prioridades siguientes

**F3 ya es la prioridad activa**, aunque no se puede declarar visualmente terminada. F2 sigue abierta sin impedir la investigación F3. Para concluir F3 se deben estudiar precisamente los **85 cambios de longitud** y las referencias de control de flujo, diseñar una reubicación con guardas independientes para SOLO estos scripts, reconstruir una ISO privada de ensayo sin desplazar otros recursos, validar integridad PSPFS/DSARC y comandos, y reproducir la introducción REAL en PPSSPP 1.20.4 con comparativa A/B. No acortar el español para que entre ni mover opcodes a ciegas. Si no hay prueba, conservar eventos aplazados.

Mientras tanto continúan las garantías: **9.237 textos** preservados, **4.524 cambios SCRIPT.DAT diferidos**, **51.705 comandos** y **1.625 inicios** con offsets protegidos, 19 glifos A1–B3 sin activar tinta blanca por defecto (`white_new_ink=False`), PR #7 en borrador, ni merge ni force push. No subir ISO, BPS, ejecutables del juego, fuentes/IMY/PNG, gameplay, RAM/GE/VRAM, vídeos ni capturas comerciales.

**Relevo recursivo:** `prompts/SIGUIENTE_TAREA.md` debe describir F3 activa, el bloque de 85, el emulador histórico y el impedimento actual, ordenar el trabajo auténtico y exigir de nuevo su propia regeneración autónoma.
