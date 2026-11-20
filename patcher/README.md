# Cladun · Parcheador BPS para Windows

Aplicación nativa para Windows 10/11 x64, sin instalador ni Python, .NET, C/Visual C++ Redistributable u otras dependencias de usuario. Compilada con Go y la API Win32 del sistema; no incluye ISO, datos ni gráficos comerciales.

## Uso

1. Descarga `Cladun-Parcheador-Windows-x64.exe` desde los artefactos de GitHub Actions del repositorio o compílalo desde el código fuente.
2. Abre el ejecutable. En **ISO original** selecciona tu copia legal de *Cladun: This Is an RPG!* USA PSP, SHA-256 `b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
3. En **Parche** selecciona un archivo `.bps` generado por el proyecto. **Todavía no se ha publicado un BPS español final validado en PPSSPP.**
4. Selecciona una ruta nueva para la ISO traducida y pulsa **Aplicar parche**.
5. Si la operación se completa, revisa el SHA-256 mostrado. Comprueba de forma independiente el funcionamiento de la ISO en PPSSPP.

El parcheador **nunca modifica la ISO fuente** y **nunca sobrescribe la ruta de salida**. Rechaza imágenes de otro SHA-256, archivos BPS corruptos y resultados cuyo CRC32 no coincida con el objetivo declarado en BPS. Es compatible con las cuatro instrucciones estándar BPS1 (SourceRead, TargetRead, SourceCopy, TargetCopy), y no carga la ISO completa en memoria.

> **Alcance de la seguridad:** los CRC32 comprueban la integridad del diferencial; por sí solos **no prueban que un BPS arbitrario conserve retratos, sprites, tiles u otros assets**. La comprobación estructural de los recursos ajenos se ejecuta en el pipeline de generación y auditoría del parche, descrito en `docs/PARCHE_BPS_EXPERIMENTAL.md`. Utiliza únicamente parches validados y publicados por el proyecto. **No se afirma que la traducción, el arranque ni los glifos estén verificados en PPSSPP.**

## Desarrollo y compilación

Desde el directorio `patcher` de este repositorio:

```bash
go test ./...
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags="-H=windowsgui -s -w" -o Cladun-Parcheador-Windows-x64.exe ./cmd/cladun-patcher
```

Se puede compilar en Windows directamente con Go, o hacer compilación cruzada desde Linux. **El usuario final no necesita Go.** La compilación automática de GitHub Actions crea el `.exe` descargable como artefacto de cada ejecución correcta del workflow `parcheador-windows.yml`.

## Limitaciones actuales

- Arquitectura de salida: **Windows x64**; no está probado en Windows x86/ARM ni mediante Wine.
- Las pruebas automatizadas del motor BPS se realizan con imágenes sintéticas. La compilación Windows se verifica como PE32+; la interfaz gráfica necesita una prueba manual en Windows real.
- El BPS español integral no está aún publicado: la integración del repositorio es experimental y sigue pendiente una ISO candidata verificada en PPSSPP.
- Los ejecutables no están firmados digitalmente; Windows puede mostrar una advertencia SmartScreen para aplicaciones nuevas no firmadas.

## Licencia y privacidad

El parcheador procesa únicamente archivos locales; no envía telemetría, no consulta la red y no redistribuye contenido protegido del juego. El proyecto no incluye imágenes comerciales de PSP.
