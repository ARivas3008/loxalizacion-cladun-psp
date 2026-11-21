> **v0.1.5 — revisión de tildes y símbolos:** se conservan las 19 letras/signos españoles de un byte y las mejoras del menú de configuración, pero se corrigen exclusivamente los glifos **¿** y **¡**, que estaban desplazados por una rotación horizontal dentro de FONT.ARC. Nuevo BPS SHA-256 `976fda78adf3e6c2c3c31d5b89bc2f04b18c0905789305b25e9d0a58bf8cea0c` y candidata `9be7b07a2c5c8c9026ffd0f829f613237f9a31e8fe2455856649ff6c1fe2b4ef`. Los iconos de botones y sangrías del menú requieren inspección visual; **no probado en PPSSPP ni aprobado como parche final**. Ver [informe](../docs/AUDITORIA_MENU_TILDES_SIMBOLOS_2026-11-20.md). Un BPS v0.1.4 no vale con el parcheador v0.1.5.

> **20/11/2026 — v0.1.4 experimental de eventos protegidos (PARCIAL):** el nuevo BPS del corpus consolidado sustituye 3.724 registros, pero pospone 4.524 diálogos que cambiarían longitudes y offsets de eventos. Conserva los offsets de 51.705 comandos originales y el códec español de un byte A1–B3. No es traducción completa ni ha pasado pruebas de esta compilación en PPSSPP. Ver [auditoría de integración](../docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md). Los hashes v0.1.3 que figuran más abajo son históricos, y su BPS no debe emplearse con v0.1.4.

# Cladun · Parcheador de ISO única (Windows x64)

Aplicación nativa Go/Win32 sin Python, C, .NET ni instalación de runtimes. La interfaz **solo pide la ISO original**. Detecta automáticamente la versión USA auditada mediante el SHA-256 completo y crea `Cladun-ES-EXPERIMENTAL.iso` en la misma carpeta. La imagen original jamás se sobrescribe.

## Importante: separación entre código público y prueba privada

**La traducción integrada es todavía EXPERIMENTAL y solo dispone de una prueba parcial de arranque en PPSSPP (menú español e inicio de partida); no existe verificación de todos los mapas, combates y textos.** Por ello:

- El repositorio público contiene la **interfaz, el motor BPS y los mecanismos de seguridad**, pero **no** incluye la ISO, el BPS español experimental ni los recursos del juego.
- El ejecutable compilado **sin** el tag `cladun_embedded` es una **vista previa de la interfaz**. Detecta la falta de payload y **bloquea la aplicación**; no representa un parche completo.
- El ejecutable **privado de pruebas** se compila incorporando un BPS ya generado y verificado por el integrador de este proyecto. Entonces sí aplica la traducción sin solicitar ningún archivo adicional. No debe publicarse como parche jugable hasta validar PPSSPP.
- La antigua versión `parcheador-v0.1.0` pedía un `.bps` por separado y además tenía una constante SHA-256 incompleta. **Está obsoleta y no debe utilizarse**.

## Corrección de «Examinar» — v0.1.1

En Windows, `GetOpenFileNameW` requiere que la lista de filtros esté representada como una cadena UTF-16 con separadores NUL. El código anterior utilizaba `syscall.StringToUTF16` sobre un texto con `\x00`, lo que provoca un **panic** en Go y cierra el programa al pulsar **Examinar**. Ahora se construye el filtro mediante `utf16.Encode` sin perder los separadores. También se informa de errores Win32 distintos de la cancelación normal, se mantienen vivos los buffers durante la llamada modal y se añadió una prueba de regresión de los filtros y del tamaño de `OPENFILENAMEW` en Windows x64.

El `.exe` privado v0.1.1 conserva el parche BPS incorporado: **solo se selecciona la ISO original**. La compilación pública de GitHub sigue siendo una vista previa sin traducción integrada, por la falta de validación en PPSSPP.

## Interfaz de usuario

1. Abrir el `.exe` experimental entregado para pruebas.
2. Pulsar **Examinar** y elegir la ISO original de *Cladun: This Is an RPG!* USA PSP.
3. Pulsar **Crear ISO de prueba**.
4. El programa valida el SHA-256 de origen, el SHA-256 de su BPS integrado, los CRC32 del parche y del resultado, y el **SHA-256 exacto de la ISO candidata auditada**. Solo después de las comprobaciones publica la salida; nunca sobrescribe la ISO original ni otra salida.
5. Abrir `Cladun-ES-EXPERIMENTAL.iso` en PPSSPP para efectuar las pruebas funcionales que faltan.

**ISO fuente aceptada:** `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f` (64 hex).

## Compilación pública, sin traducción no aprobada

```sh
cd patcher
go test ./...
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags="-H=windowsgui -s -w" -o Cladun-Interfaz-Sin-Parche.exe ./cmd/cladun-patcher
```

La compilación sin payload deshabilita el botón para evitar generar falsas ISOs traducidas.

## Compilación PRIVADA para probar un BPS experimental auditado

El desarrollador debe crear **localmente**, a partir de una ISO propia, el parche experimental de acuerdo con `docs/PARCHE_BPS_EXPERIMENTAL.md` y las verificaciones correspondientes. **No añadir el BPS, ISO ni sus recursos al repositorio.** La opción `cladun_embedded` exige explícitamente que el archivo `patcher/cmd/cladun-patcher/traduccion_es_experimental.bps` exista en el árbol privado; ese archivo queda ignorado por Git. El componente `internal/automatic/apply.go` rechaza cualquier BPS cuyo SHA-256 difiera del previsto y cualquier resultado cuyo SHA-256 no coincida con la ISO candidata validada estáticamente.

```sh
cd patcher
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -tags cladun_embedded -trimpath -ldflags="-H=windowsgui -s -w" -o Cladun-Parcheador-ISO-Unica-EXPERIMENTAL.exe ./cmd/cladun-patcher
```

En Windows, la compilación privada puede usar `go build -tags cladun_embedded` desde el mismo directorio. **El usuario final no necesita Go.**

## Diagnóstico de bloqueo `NOW LOADING` y versión v0.1.2

**No usar la versión v0.1.1.** La candidata anterior reempaquetaba las seis PNG de `SYS.DAT2` mediante anexado a un segundo bloque, creciendo de 350.720 a aproximadamente 701.932 bytes. La ejecución mostraba llamadas GPU a direcciones ilegales y no avanzaba con normalidad. Los controles de aislamiento estático por sí solos no detectaban la incompatibilidad runtime.

En v0.1.2 el integrador reconstruye las seis PNG de texto **dentro del mismo slot físico de `SYS.DAT2`**, con alineación de 512 bytes, sin duplicar las imágenes. Los bytes no textuales fuera de los cuatro contenedores modificados se conservan. `SYS.DAT2` permanece en el offset PSPFS `3035136` y ocupa `351232` bytes, dentro de la capacidad original. El nuevo BPS experimental integrado es obligatorio para esta versión: el programa verifica su SHA-256 y el SHA-256 de la ISO resultante.

**Hashes de la nueva candidata privada (no publicar la ISO):**

- SHA-256 ISO original: `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`
- SHA-256 BPS integrado v0.1.2: `b913cb5509f22721ff533f88848facdc894a3047b66a2597aaa7f333741d69e0`
- SHA-256 candidata v0.1.2: `27864a48787e54dff7e211214becf26ddbc688a84a1cf78fb444686a8e475f18`

**Resultados de la prueba de ejecución:** se compararon la ISO original, la candidata defectuosa y las variantes aisladas de `SYS.DAT2`, fuente y script en PPSSPP 1.20.4 Linux (software rendering). La corrección compacta avanzó a menú con «Comenzar», «Continuar» y «Opciones»; tras seleccionar «Comenzar», presentó la configuración de música y el siguiente segmento de introducción. Durante la prueba combinada no se observaron mensajes `GPUCommon CALL to illegal address`. **No equivale a una validación completa** del juego ni de la traducción; faltan personaje, mapas, combate, partidas guardadas y pruebas prolongadas.

[Informe detallado de diagnóstico y reproducción](../docs/DIAGNOSTICO_NOW_LOADING_2026-11-20.md).

La herramienta no transmite datos por red, no incluye telemetría y no distribuye archivos comerciales de juego en el código público. El `.exe` privado no está firmado digitalmente. Windows puede mostrar SmartScreen.


## Actualización v0.1.3 — traducción revisada + caracteres españoles compactos

La compilación **Cladun-Parcheador-ES-v0.1.3-Windows-x64.exe** incluye un
único parche diferencial BPS de la ISO USA, sin pedir archivos adicionales.
Requiere la ISO original cuyo SHA-256 es `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
Verifica la integridad y produce la ISO experimental de SHA-256
`6d874a2e04fa9b27c14cbc42a49e91308d82c802b3f247ac1f0f1841953dd261`.
El diferencial incorporado tiene SHA-256
`300f0eabccf7bf64b2d1eb0e783d31a213f62fdc006ac193fad2918b23e92b80`.

**Cambios:** actualización del español tras auditoría estática de las 9.237
unidades, fuente de 19 glifos españoles en el rango de un byte `0xA1..0xB3`
en vez de los códigos de dos bytes `0xF5A0..0xF5B2`, conservación exacta
de los 2.721 glifos de origen y verificación binaria de los 345 archivos
PSPFS fuera de los contenedores de localización.

**Verificación PPSSPP:** arranque, menú, selección musical y continuación a
los diálogos iniciales; en pantalla se leen **música** y **configuración**
sin el espacio introducido por el códec anterior. **No** se han completado
todas las misiones, mapas, combates, guardados ni todas las pantallas. Por
ello se publica como *experimental/pre-release* y no como traducción final.

La rama `revision-manual-dialogos` conserva el glosario, los 9.237 IDs,
los TXT bilingües, los informes y el código de regeneración.

**Compilación reproducible de la versión experimental** (sin la ISO comercial):

```sh
cd patcher
go test ./...
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -tags cladun_embedded -trimpath -ldflags='-H=windowsgui -s -w' -o Cladun-Parcheador-ES-v0.1.3-Windows-x64.exe ./cmd/cladun-patcher
```

El `.bps` solo contiene el diferencial necesario para reconstruir la ISO
traducida a partir de una copia legítima; **no se distribuye la ISO comercial**.
Las advertencias históricas de v0.1.2 conservadas arriba no describen la
compilación actual. Véase [validación v0.1.3](../docs/PPSSPP_CARACTERES_ES_Y_PARCEHADO_2026-11-20.md).
