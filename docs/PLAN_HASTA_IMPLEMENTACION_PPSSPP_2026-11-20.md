# Ruta de implementación verificable de Cladun ES — 20/11/2026

**Estado:** v0.1.5 EXPERIMENTAL PARCIAL. Base: `integracion-eventos-segura-20261120`; [PR de trabajo #7](https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7), sin fusionar. Esta guía resume el plan operativo; el documento de entrega ampliado de la conversación incluye tablas, comandos y procedimientos detallados.

## Comprobación real y límites

Se ejecutaron original USA y candidato v0.1.5 en PPSSPP 1.20.4 Linux x86_64 (software/llvmpipe, Xvfb 1280×720, ventana 960×544). El juego parcheado llega al título, a «Opciones», a la selección musical y a la introducción. «música» y «configuración» se muestran sin espacios tras la vocal. Pero el cuadro de configuración mide aproximadamente **333 px de anchura frente a 764 px en el original**, con rótulos/valores amontonados. La introducción aún muestra inglés. Los iconos de botones y signos de apertura «¿¡» no se han comprobado exhaustivamente en pantalla; ni nivel 2, ni enciclopedia, combate, mapa completo, ni guardado. El EXE Windows no se ha ejecutado: se aplicó el BPS.

**Paquete de capturas privadas**, entregado en la conversación: `Evidencias_reales_PPSSPP_Cladun_ES_v015.zip`. Sus nombres son: `01_menu_principal_v015.png`, `02_configuracion_original_USA.png`, `03_configuracion_parche_v015.png`, `04_comparacion_original_vs_v015.png`, `05_opcion_musica_y_tilde.png`, `06_inicio_partida_seleccion_musica.png`, `07_intro_ingles_aun_visible.png`, `08_intro_animacion_sin_audio.mp4`. El ZIP incluye informe y hashes. **No se subieron activos comerciales a GitHub.**

Hashes SHA-256: ISO USA `b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f`, candidata v0.1.5 `9be7b07a2c5c8c9026ffd0f829f613237f9a31e8fe2455856649ff6c1fe2b4ef`, BPS v0.1.5 `976fda78adf3e6c2c3c31d5b89bc2f04b18c0905789305b25e9d0a58bf8cea0c`. Solo se distribuyen deltas y ejecutables experimentales privados por separado, no ISOs.

## Rutas y recursos para trabajar

| Trabajo | Ruta del repositorio o recurso de la ISO |
|---|---|
| Reglas y prioridades | `AGENTS.md`, `README.md`, `docs/AUDITORIA_MENU_TILDES_SIMBOLOS_2026-11-20.md`, `docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md` |
| Originales inmutables | `corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv`: 9.237 registros |
| Traducción y glosario | `traduccion/CLADUN_BORRADOR_ES.csv`, sus TXT y `traduccion/GLOSARIO_CANONICO.csv` |
| Menú | IDs `005687–005718`, especialmente `005695, 005696, 005697, 005698, 005709, 005713` en `DATABASE.DAT/STRTBL.DAT` |
| Fuente real v0.1.5 | `tools/charset_es.py`, `tools/font_es_narrow.py`, `tools/font_es_patch.py`, `tools/font_es_guard.py` |
| Scripts y eventos | `tools/integrar_parche_seguro.py`, `tools/script_event_guard.py`, `tests/test_script_event_guard.py` |
| Recursos y empaquetado | `tools/extract_cladun.py`, `tools/imy_repack_safe.py`, `tools/graficos_texto_es.py` |
| Integridad y parche | `tools/verificar_integridad.py`, `tools/verificar_borrador_es.py`, `tools/generar_parche_bps.py` |
| Aplicación Windows | `patcher/internal/automatic/apply.go` y `patcher/cmd/cladun-patcher/main_windows.go` |
| Informes de base | `reports/auditoria_menu_signos_v015_2026-11-20.json`, `reports/integracion_eventos_protegidos_2026-11-20.json` |
| CI | `.github/workflows/validacion-integracion-eventos.yml` |
| Estado y continuidad | `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y `prompts/PROMPT_INICIAL_CORRECCION_PPSSPP.md` |

Dentro de la ISO, `PSP_GAME/USRDIR/DATA.DAT` es un contenedor de **349 entradas PSPFS**. `SCRIPT.SDT` contiene `SCRIPT.DAT` y `SCRIPT.TBL`; la base de datos incluye `DATABASE.DAT`/`STRTBL.DAT`, la fuente `FONT.ARC` con `FONT.BIN` y seis atlas IMY, y los seis PNG textuales están en `SYS.DAT2`. Los nombres en la ISO **no son rutas sueltas de GitHub**.

**Distinguir versiones:** el antiguo prototipo F5A0–F5B2 era de dos bytes y separaba tildes al dibujarlas; el códec v0.1.5 usa 19 posiciones **de un byte A1–B3**. La rotación de «¿¡» dentro de la celda de 16px se corrigió en v0.1.5, sin prueba exhaustiva en pantalla. Agregar 19 registros antes de los no ASCII desplaza físicamente 2.626 glifos y 19 índices los símbolos de botones (por código los dibujos están preservados). **La hipótesis de que el motor usa índices fijos no está verificada**.

## Secuencia de trabajo sin saltos

### F1 / prioridad P0: reparar anchura y alineación de Opciones (tarea inmediata)

**Motivo:** original ≈764 px, parche ≈333 px. **Causa no determinada**: podrían intervenir espacios ideográficos perdidos, métricas, etiquetas reducidas, cálculo dinámico de ventana o recursos de interfaz. No afirmar que las tildes provocan esta diferencia.

**Método:** mostrar cadenas y espacios con `repr` por IDs 005687–005718; medir avance con métricas de `FONT.BIN`, observar conservaciones de `%2d`; comparar versiones con modificaciones aisladas de DB sola, fuente sola, `SYS.DAT2` solo y combinaciones; ejecutar ISO original y cada candidata en PPSSPP a igual resolución. Investigar dimensión de ventana en el motor si el espaciado no explica el fenómeno. No rellenar arbitrariamente con espacios, no alterar opcodes ni tocar sprites/retratos. Proteger «Vol. efectos», «Vol. música», «Tipo música», «Controles» y textos de ayuda ya mejorados. **Criterio de salida:** todos los valores, cursor y opciones legibles, sin colisiones o recorte, capturas originales vs reparación y pruebas de regresión.

### F2 / prioridad P1: índice real de iconos y glifos

Comparar «⑪», «⑫», «△», «□», «×», etc. en opciones y escenas contra la original. Determinar si el motor usa búsqueda por código CP932 o índice directo. Medir glifos A1–B3, incluyendo `¿¡áéíóúÁÉÍÓÚñÑüÜ«»ō`. No declarar símbolos correctos solo por coincidencia de su dibujo en atlas. **Salida:** matriz de símbolos y capturas reales sin desfases.

### F3 / prioridad P0: intro en inglés

Transcribir frase exacta de la captura `07_intro_ingles_aun_visible.png`, buscar `grupo_id` y origen del texto en CSV y después identificar si procede de un script pospuesto, rótulo gráfico u otro recurso. No inventar el ID ni la causa. Traducir tras asegurar que el flujo de eventos, los nombres y los retratos siguen funcionando. **Salida:** captura de esa misma escena en español y trazabilidad origen→recurso→cambio.

### F4 / prioridad P0: 4.524 cambios de script aplazados

Actualmente solo se insertaron **376** cambios de script de la misma longitud y se aplazaron **4.524** cambios con longitud distinta para conservar offsets. Son 51.705 comandos (46.308 no textuales) y 1.625 scripts. La antigua reconstrucción de longitud variable desplazaba **51.555** comandos, incluidos **46.164** no textuales, aun preservando bytes. Localizar referencias a offsets en `SCRIPT.TBL`, `SCRIPT.DAT` y en el intérprete; demostrar modelo de saltos antes de permitir reubicación. Alternativas (almacenamiento aparte, tablas de referencias, etc.) son **hipótesis** hasta prueba. **Salida:** integración justificada con regresión de comandos y escenas, o lista de bloqueos por ID sin saltarse guardas.

### F5 / prioridad P1: recorrido funcional

Probar primera escena, menús, personaje/equipos, mapas, primer combate, eventos, segundo nivel, enciclopedia, guardado/carga, retratos, sonido y retorno a menú. Para cada flujo guardar pasos, PPSSPP y versión, original/parche, captura/log, conclusión. No llamar «completo» al juego por arrancar.

### F6: BPS, EXE, documentación y lanzamiento

Tras revalidar exactitud, BPS roundtrip e integridad, ajustar hashes de `patcher/internal/automatic/apply.go` y compilar EXE privado Windows x64 con payload fuera de Git. Verificar también el EXE en Windows real o VM. Mantener el PR en borrador mientras existan incidencias de juego. Publicar solo código/documentación en Git, no ISO, BPS ni archivos gráficos comerciales.

## Comandos auditables

```bash
git clone https://github.com/ARivas3008/loxalizacion-cladun-psp.git
cd loxalizacion-cladun-psp
git switch integracion-eventos-segura-20261120
git switch -c fix/menu-configuracion-v016
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'Pillow>=12,<14'
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
```

Para una **ISO original privada exacta** (definir rutas en un directorio nuevo; ningún archivo de salida debe preexistir):

```bash
export ISO_ORIGINAL='/ruta/privada/Cladun-USA.iso'
export ISO_CANDIDATA='/ruta/privada/v016/Cladun-ES-v016.iso'
export REP_INTEGRACION='/ruta/privada/v016/integracion.json'
export BPS_CANDIDATO='/ruta/privada/v016/Cladun-ES-v016-EXPERIMENTAL.bps'
export REP_BPS='/ruta/privada/v016/bps.json'
sha256sum "$ISO_ORIGINAL"
python tools/integrar_parche_seguro.py --iso "$ISO_ORIGINAL" --candidate "$ISO_CANDIDATA" --report "$REP_INTEGRACION" --experimental-parcial --event-safe-only
python tools/generar_parche_bps.py --original "$ISO_ORIGINAL" --candidato "$ISO_CANDIDATA" --informe-integracion "$REP_INTEGRACION" --salida "$BPS_CANDIDATO" --informe-bps "$REP_BPS" --experimental --event-safe-only
sha256sum "$ISO_CANDIDATA" "$BPS_CANDIDATO"
```

Estos comandos generan **candidatos parciales** y no reinsertan automáticamente los 4.524 textos protegidos. No quitar `--event-safe-only` por conveniencia. Para pruebas aisladas usar `python -m unittest tests.test_script_event_guard -v`, `tests.test_signos_invertidos` y `tests.test_charset_es`. Para buscar registros en el CSV: leer `traduccion/CLADUN_BORRADOR_ES.csv` mediante `csv.DictReader(..., encoding='utf-8-sig')` y mostrar `repr` de original/espanol. La ruta de PPSSPP depende del equipo: comprobar `command -v PPSSPPSDL` o `command -v PPSSPPQt`; no inventarla.

**Compilación Go pública sin payload**: `cd patcher && GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags='-H=windowsgui -s -w' -o /tmp/cladun-interfaz.exe ./cmd/cladun-patcher`. Para variante privada, **primero** actualizar SHA-256 BPS/destino en `apply.go` y probar roundtrip, copiar BPS a `patcher/cmd/cladun-patcher/traduccion_es_experimental.bps` (ignorado por Git), probar `go test -tags cladun_embedded ./...` y compilar con `-tags cladun_embedded`. No versionar el payload.

## Contrato de entrega de cada iteración

**Siempre:** (1) cambios y causa demostrada; (2) capturas PPSSPP reales frente al original o bloqueo explícito; (3) tests/comandos y hashes; (4) estado por incidencia y cobertura; (5) commit y PR verificados; (6) actualización de `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y **nuevo archivo `prompts/SIGUIENTE_TAREA.md`** con un prompt *autónomo* para la fase siguiente: archivos, IDs, problemas, evidencias, comandos, SHA, riesgos y restricciones; y la **misma exigencia recursiva de generar otro prompt al terminar**. Si F1 no acaba, el siguiente prompt debe continuar F1. No fingir finalización ni cerrar el PR sin pruebas.
