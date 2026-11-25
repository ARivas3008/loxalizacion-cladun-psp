# F3 — Topología IMY original ANIME000: intervalos, secuencias y repeticiones (23/11/2026)

**Evidencia A original, B tests sintéticos; NO se generó evidencia C PPSSPP en este relevo. F3 ABIERTA; F2 ABIERTA.**

Se extrajo de nuevo el ISO USA aportado por el usuario (305.496.064 bytes; SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`) usando libarchive.so.13. No se modificó ni distribuyó. El archivo original contiene 349 PSPFS; se validaron nombre, tamaño y SHA de ANIME000.IDT (234), ANIME001.LDT (235), ANIME002.LDT (236).

## Resultado verificado en bytes originales

| Recurso | Firmas IMY | Tipos | Rachas más largas | Repeticiones de intervalos exactos |
| --- | ---: | --- | --- | ---: |
| ANIME000.IDT | 231 | 136 de 0x00; 95 de 0x02 | 0x00: 101; 0x02: 36 | 17 de 0x02; 0 de 0x00 |
| ANIME001.LDT | 24 | 24 de 0x00 | 0x00: 24 | 0 |
| ANIME002.LDT | 0 | ninguna firma literal | no aplica | 0 |

En ANIME000 hay 31 rachas; transiciones consecutivas: `00→00=121`, `00→02=15`, `02→00=15`, `02→02=79`. Las 255 cabeceras originales están alineadas a cuatro bytes y el intervalo de flags de cada una no invade la siguiente cabecera encontrada. En ANIME000 la primera cabecera empieza en offset **7568**; existe un intervalo entre esa cabecera y la siguiente de **1211392 bytes**. Es una observación de límites, NO una unidad de imagen certificada. Las 17 repeticiones significan 17 intervalos adicionales byte-idénticos, NO 17 fotogramas ni animaciones identificados.

**Limitación esencial:** localizar cadenas `IMY\0` y comprobar intervalos adyacentes no demuestra el índice real de contenedor, la semántica de referencias a fotogramas, la descompresión de tipo 0x02, las paletas, ni la ubicación del texto inglés del prólogo. El ensayo anterior de flags tipo 0x02 (95/95 incompatibles) se mantiene sin cambios. No añadir un decodificador 0x02 especulativo.

## Código y QA

- Herramienta de solo lectura `tools/f3_anime_topologia.py`, que exige SHA y tamaño exactos de la ISO USA, valida los SHA de tres miembros, PSPFS/349, geometría/flags, y produce solo métricas y agregados sin exportar bytes ni imágenes.
- Pruebas `tests/test_f3_anime_topologia.py`: **14 PASS** local sobre datos sintéticos. Suite integral en checkout: pendiente de CI; sin checkout local por error DNS al intentar `git ls-remote`.
- Informe público `reports/RESULTADO_F3_ANIME_TOPOLOGIA_2026-11-23.json` y JSON privado generado en la sesión SHA256 `5cb78034a1495497a874a4f502dd21eaa07b2ac5796c392e4ea7db1539fa04e6`.

Comandos (fuera de Git y con binarios PRIVADOS):

    python tools/f3_anime_topologia.py --iso-original /PRIVADO/USA_original.iso --reporte-privado /PRIVADO/topologia_nueva.json
    python -m unittest discover -s tests -p 'test_f3_anime_topologia.py' -v

El hash de ISO/miembros y las 14 pruebas corresponden a esta ejecución; no se reinició PPSSPP 1.20.4, no hay capturas ni dumps GE nuevos. Las pruebas de código no certifican el prólogo, el emulador, la liberación de 85 eventos ni la corrección de 19 glifos.

## Continuidad sin regresiones

El PR #7 debe seguir ABIERTO/DRAFT. Conservar los cambios F2 paralelos `tools/f2_ruta_ws_liberacion_segura.py` y documentación F2 del mapa real, así como los 97 textos demo1001 traducidos (85 de longitud cambiante BLOQUEADOS), 4.524 SCRIPT.DAT pendientes, 51.705 comandos, 46.308 no textuales, 1.625 scripts, 349 PSPFS, `--event-safe-only`, `white_new_ink=False`. Ningún cambio al corpus, a ISO comercial, a IMY, a tipos MIPS ni al parcheador.

Para identificar la fuente visual: PPSSPP oficial autenticado y prólogo en vivo con traza PSP I/O+CPU+GE+VRAM o sonda cromática no disruptiva y A/B sincronizado, NUNCA inferencia basada únicamente en el nombre ANIME000. En paralelo investigar semántica de destinos de saltos en 85 eventos sin mover un offset antes de las pruebas.
