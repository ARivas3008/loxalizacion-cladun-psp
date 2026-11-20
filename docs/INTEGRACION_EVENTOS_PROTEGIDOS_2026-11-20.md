# Integración española con offsets de eventos protegidos — 20/11/2026

**Estado: compilación EXPERIMENTAL PARCIAL. No se ha probado esta compilación en PPSSPP ni en PSP. No equivale a la traducción completa.**

## Diagnóstico

La reconstrucción completa del corpus consolidado planifica 8.248 sustituciones binarias de 9.237 registros. En SCRIPT.DAT, 4.900 diálogos cambian bytes y 4.524 cambian longitud. La reconstrucción completa conserva los 46.308 opcodes no textuales, sus argumentos e IDs, pero **desplaza 51.555 comandos (46.164 no textuales) y 1.615 comienzos de script**. Es posible que existan referencias internas a esas posiciones. Esto no demuestra que sean la causa de fallos del segundo nivel o la enciclopedia, pero impide certificar esa inserción como segura.

El modo nuevo de protección exige sustituir exclusivamente diálogos con **igual longitud en bytes**. Su auditoría comprueba cada comando y todos los offsets contra el original.

## Comprobaciones sobre la ISO USA exacta

| Invariante | Valor |
|---|---:|
| Registros originales cotejados | 9.237 |
| Sustituciones binarias integradas en esta compilación | **3.724** |
| Registros que ya coinciden en bytes | 989 |
| Sustituciones de diálogo pendientes por longitud distinta | **4.524** |
| Diálogos cambiados con longitud fija | **376** |
| Comandos de script comprobados | **51.705** |
| Comandos no textuales intactos | **46.308** |
| Comandos cuyo offset cambió | **0** |
| Comienzos de script desplazados | **0** |
| Recursos PSPFS ajenos a los cuatro contenedores traducidos | **345** íntegros |
| Glifos españoles | 19, códigos de un byte A1–B3 |
| Glifos originales | 2.721 conservados por la comprobación de fuente |
| Nueva candidata validada en PPSSPP | **NO** |

Los 4.524 diálogos pendientes **siguen traducidos en el CSV maestro**. No se han borrado, reordenado, abreviado ni sobrescrito. Se aplaza su inserción hasta verificar el modelo de referencias del intérprete y las rutas de ejecución.

## Manifiesto SHA-256

- ISO fuente USA: b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f.
- ISO candidata privada: 7d7d598c719500deaf58cb8535106396745221da16f39ee9e3a2530f92da9fc8.
- BPS experimental: cbb3dfe5882524cc0f98e0f0007cfb63bec26abdbae6249fc07077d37d4ad9af.
- EXE experimental Windows x64: 8dc323bbbafa09ef99e5e8a3738148df2c94900551641e9fda14093415ca320e.

El BPS se aplicó a la fuente y se verificó la reconstrucción exacta del SHA-256 de la candidata. Los recursos PSPFS no modificados y los archivos ISO9660 ajenos conservaron bytes y posiciones. El EXE comprueba SHA-256 de fuente, BPS y resultado, y no sobrescribe ISO originales ni archivos existentes.

## Reconstrucción local (solo con ISO propia)

~~~bash
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py

python tools/integrar_parche_seguro.py \
  --iso ORIGINAL-USA.iso \
  --candidate CANDIDATA-PRIVADA.iso \
  --report integracion-privada.json \
  --experimental-parcial --event-safe-only

python tools/generar_parche_bps.py \
  --original ORIGINAL-USA.iso \
  --candidato CANDIDATA-PRIVADA.iso \
  --informe-integracion integracion-privada.json \
  --salida traduccion_es_experimental.bps \
  --informe-bps verificacion-bps.json \
  --experimental --event-safe-only
~~~

Para compilar el EXE de prueba, colocar localmente el BPS en patcher/cmd/cladun-patcher/traduccion_es_experimental.bps (sin añadirlo a GitHub) y, desde patcher/, ejecutar:

~~~bash
go test ./...
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -tags cladun_embedded \
  -trimpath -ldflags="-H=windowsgui -s -w" \
  -o Cladun-Parcheador-ES-v0.1.4-EXPERIMENTAL.exe ./cmd/cladun-patcher
~~~

## Límites que impiden certificar el juego

Esta versión **no** incorpora las 4.524 traducciones que cambiarían offsets de comando. No se ha ejecutado su interfaz en Windows ni la nueva ISO en PPSSPP. No se han comprobado las transiciones del segundo nivel, la enciclopedia, todas las escenas, menús, combates y guardado/carga. La fuente de un byte mantiene el arreglo del espaciado de acentos del proyecto, pero tampoco se ha confirmado visualmente en esta compilación.

La reconstrucción completa sigue siendo una vía **experimental de ingeniería inversa**, no un parche de jugabilidad certificada. No publicar ni fusionar como versión estable sin pruebas de PPSSPP sobre los eventos conflictivos.
