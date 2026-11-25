# CLADUN ES — F4 R13: grafo de enlaces numéricos del prólogo (23/11/2026)

**Estado:** auditoría A de la ISO auténtica + tests B sintéticos; PPSSPP C NO EJECUTADO. No se modificó ISO, SCRIPT.DAT/TBL, fuentes, textures ni BPS. Este documento registra **posibles enlaces numéricos**, jamás saltos MIPS demostrados.

## Origen y autenticación

ISO USA: **305.496.064 bytes**; SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. DATA.DAT PSPFS: 349. SCRIPT.DAT SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, SCRIPT.TBL SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. El reparseo completo autentica **1.625 bloques, 51.705 comandos, 46.308 no textuales**. Herramienta `tools/f4_r13_grafo_intro.py` y pruebas `tests/test_f4_r13_grafo_intro.py` (**18 PASS B local**, compilación/suite completa solo mediante CI cuando esté publicada). Informe privado independiente de metadatos SHA256 `ca08137b06cdbb3a9d065a69bae7a552f3fdf393d8f567e2287f64085e7b25dd`.

## Cinco enlaces del prólogo que discriminan IDs literales de IDs con desplazamiento +100

| Bloque/orden origen | Op | Argumento u32 | Destino candidato `valor−100` | Destino literal |
|---|---|---:|---|---|
| 20/20 | 0x0A | 100100 | 757 | 758 |
| 757/2 | 0x0A | 100200 | 758 | 764 |
| 758/1 | 0x0C | 100290 | 759 | 765 |
| 758/416 | 0x0A | 100201 | 760 | 766 |
| 760/1 | 0x0C | 100291 | 761 | inexistente |

En particular, **`scr01.dsf` bloque20 orden20 → bloque757 → bloque758** bajo la transformación candidata, y `demo1001_00.dsf` bloque758 enlaza numéricamente con 759 (`0x0C`) y 760 (`0x0A`). La interpretación literal del enlace de bloque757 seleccionaría bloque764 (`demo1002_00.dsf`), no bloque758; y el `0x0C` de bloque758 seleccionaría 765, no 759. Es un contraste fuerte a favor del modelo estático **pero no prueba que el intérprete ejecute esos saltos**. Offset original de la instrucción inicial: decimal 7420 en SCRIPT.DAT; NO es dirección de RAM.

## Perfil completo de referencias numéricas por tipo de opcode

| Op | Total | ID al restar 100 | Mismo nombre de fichero entre orígenes/destinos | Mismo bloque |
|---|---:|---:|---:|---:|
| 0x0A | 862 | 860 | 86 | 0 |
| 0x0B | 166 | 158 | 142 | 0 |
| 0x0C | 102 | 66 | 64 | 0 |

El porcentaje de coincidencias con **mismo nombre de script** es especialmente alto en `0x0B` y `0x0C`, pero no demuestra que las instrucciones sean llamadas internas o retornos. En el propio prólogo, los bloques 758 y 760 contienen un `0x0C` cuyo argumento−100 es un ID de script existente y **otro `0x0C` con argumento 100**, de significado desconocido. Los bloques 759 y 761 contienen solo el `0x0C` de argumento 100 dentro de este subconjunto.

El perfil mantiene sin coincidencia: `0x0A` valores 0/1 (2), `0x0B` valor 3 (8), `0x0C` valor 100 (36). Ninguno se etiqueta como centinela sin evidencia C.

## Por qué falta ejecución real

Este turno confirmó que el archivo `PSP_GAME/SYSDIR/EBOOT.BIN` empieza por `~PSP`, formato PSP protegido, y el `BOOT.BIN` comienza con 48 bytes nulos; esto **no permite inferir PCs MIPS ejecutados**. No está instalado PPSSPP oficial 1.20.4 y falló la consulta de su AppImage en github.com: `curl: (6) Could not resolve host: github.com`. La evidencia necesaria sigue siendo una sesión oficial de PPSSPP con ISO original SHA autenticada, PID/starttime, FD de ISO, WebSocket del mismo proceso y trace real de dispatch.

## Ejecutar en checkout con copia propia auténtica y salida privada

```bash
python -m unittest discover -s tests -p 'test_f4_r13_grafo_intro.py' -v
python tools/f4_r13_grafo_intro.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F4_R13_GRAFO_NUEVO.json
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed # debe devolver no cero
```

Las siguientes comprobaciones dinámicas se añaden como **Q050 y Q051 en estado NOT_RUN**. Se conservan 85 diálogos variables demo1001 y 4.524 cambios globales aplazados bajo `--event-safe-only`, fuente 2.721+19 glifos A1–B3, `white_new_ink=False`, protección CLUT2/TUIKA y PR #7 DRAFT. No publicar ISO, EBOOT, capturas, BPS comercial, dumps RAM/VRAM/GE ni texturas.
