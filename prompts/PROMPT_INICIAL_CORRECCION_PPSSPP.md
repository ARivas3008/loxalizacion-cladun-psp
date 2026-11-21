# Prompt de inicio de la implementación: corregir Cladun v0.1.5 en PPSSPP

Actúa como ingeniero senior de localización PSP, reversión de formatos binarios, QA en PPSSPP y parcheadores BPS/Go. **Ejecuta la tarea con código, pruebas y evidencias verificables**, no entregues solo una explicación. Trabaja por fases para alcanzar una localización española visualmente correcta y funcional que **no rompa eventos, retratos, sprites, tiles, mapa, combate ni otros recursos**. Al concluir tu etapa debes generar **otro prompt nuevo, autónomo y listo para pegar**, guardar `prompts/SIGUIENTE_TAREA.md` en GitHub y mostrar su texto. **Esta obligación debe repetirse dentro del nuevo prompt** para todas las etapas posteriores.

## Contexto concreto, no inventar

- Repo: https://github.com/ARivas3008/loxalizacion-cladun-psp
- Rama: `integracion-eventos-segura-20261120`, PR borrador #7 frente a `revision-manual-dialogos`. Trabaja en rama hija o en ese PR de forma revisable y conserva lo existente.
- Antes de cambiar archivos lee `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/AUDITORIA_MENU_TILDES_SIMBOLOS_2026-11-20.md`, `docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md`, `patcher/README.md`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y `tests/`.
- ISO USA original privada exacta SHA-256 `b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f`; candidata v0.1.5 `9be7b07a2c5c8c9026ffd0f829f613237f9a31e8fe2455856649ff6c1fe2b4ef`; BPS v0.1.5 `976fda78adf3e6c2c3c31d5b89bc2f04b18c0905789305b25e9d0a58bf8cea0c`. Nunca compartir en Git la ISO, archivos comerciales extraídos, fuente, BPS o EXE con payload.
- Evidencias REALES de PPSSPP 1.20.4: el ZIP privado `Evidencias_reales_PPSSPP_Cladun_ES_v015.zip` con capturas 01–07 y vídeo 08; informe `INFORME_EVIDENCIAS_PPSSPP_v015.md`, aportados en la conversación. 02 es opciones USA, 03 opciones parcheadas, 04 comparación, 05 texto con «música», 06 comienzo y 07 introducción con inglés. **No están dentro de GitHub**.
- Estado verificado: arranca, muestra título/«Opciones»/comienzo; «música» y «configuración» aparecen sin espacios. La caja de opciones pasa de anchura aproximada **764 px (original) a 333 px (parche)** y sus etiquetas/valores se amontonan. La introducción contiene frases en inglés. El atlas agrega 19 caracteres A1–B3 y desplaza +19 índices físicos de 2.626 glifos originales: **no se ha probado que el motor use índices fijos**. «¿» y «¡» fueron recolocados dentro de la celda en v0.1.5, pero no comprobados exhaustivamente en escenas. Hay **4.524 traducciones de script de distinta longitud aplazadas**: preservan offsets. La reconstrucción completa anterior desplazaba 51.555 comandos, con riesgos para eventos. No afirmar que las pantallas iniciales prueban todos los eventos.

## EJECUTA AHORA F1 — diagnóstico y reparación del menú de configuración

1. Abre en PPSSPP original USA y v0.1.5, mismo renderizador/ventana. Reproduce paso a paso «Opciones», navega y captura ambas pantallas para tener prueba antes/después. Si no puedes usar PPSSPP, explica qué evidencia falta en vez de inventar capturas.
2. Examina el CSV `traduccion/CLADUN_BORRADOR_ES.csv` y el recurso `DATABASE.DAT/STRTBL.DAT` en **IDs 005687–005718**, en especial `005695` (Retro), `005696` (Real), `005697` (%2d), `005698` (Correr), `005709` (Decimales de daño), `005713` (APAGADO). Muestra los textos originales y el español con `repr()` y mide los espacios ASCII/ideográficos y el avance de FONT.BIN. Conserva «Vol. efectos», «Vol. música», «Tipo música», «Controles» y los textos de ayuda consolidados; no alteres variables, IDs, originales ni offsets fuente.
3. Identifica **por qué** se comprime la ventana. Compara con candidatos binarios aislados: solo DB, solo fuente, solo SYS.DAT2, combinaciones y original; conserva PSPFS/DSARC y assets ajenos. Considera hipótesis de espacios, métricas y cálculo dinámico de ancho, pero no las declares causas sin prueba. Si hace falta, analiza la función del motor que mide texto/ventanas.
4. Implementa corrección mínima verificable. Ejecuta las pruebas automatizadas, auditoría de integración, verificación BPS y capturas REALES en PPSSPP: todas las opciones y valores deben ser legibles, sin clipping, solapamiento ni símbolos rotos; verificar selección/cursor/ayudas. No parchees opcodes ni datos de sprites/tiles.
5. Compara antes/después con medidas. Si el problema no queda resuelto, documenta causas comprobadas/descartadas y el próximo experimento ejecutable. Deja evidencias y código material, sin afirmar éxito ficticio.

## Qué continúa al cerrar F1

F2: glifos/atlas/«¿¡» y símbolos de botones (`⑪⑫○△□×`), inspección de accesos por código e índice; pruebas visuales originales y candidatas. F3: localizar **origen real** de frases inglesas de la introducción (script/tabla/gráfico/vídeo), traducirlas sin romper eventos. F4: investigar referencias de control para recuperar las **4.524 traducciones** aplazadas sin saltarse seguridad. F5: verificar nivel 2, enciclopedia, combate, mapas, retratos, inventarios, guardado/carga y eventos. F6: generar BPS, actualizar SHA de `patcher/internal/automatic/apply.go`, compilar/verificar EXE Windows x64 privado, cierre de documentación y evaluación final. **Si F1 no concluye, el prompt siguiente debe continuar F1**, no avanzar falsamente.

## Rutas y comandos (usar ISO privada, nunca subirla)

```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git switch -c fix/menu-configuracion-v016
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
python -m unittest tests.test_script_event_guard -v
python -m unittest tests.test_signos_invertidos -v
(cd patcher && go test ./...)
# Definir ISO_ORIGINAL, ISO_CANDIDATA, REP_INTEGRACION, BPS_CANDIDATO y REP_BPS
# con rutas privadas y nombres de salida inexistentes:
sha256sum "$ISO_ORIGINAL"
python tools/integrar_parche_seguro.py --iso "$ISO_ORIGINAL" --candidate "$ISO_CANDIDATA" --report "$REP_INTEGRACION" --experimental-parcial --event-safe-only
python tools/generar_parche_bps.py --original "$ISO_ORIGINAL" --candidato "$ISO_CANDIDATA" --informe-integracion "$REP_INTEGRACION" --salida "$BPS_CANDIDATO" --informe-bps "$REP_BPS" --experimental --event-safe-only
sha256sum "$ISO_CANDIDATA" "$BPS_CANDIDATO"
git diff --check
```

**No** quitar `--event-safe-only` para mostrar más textos sin modelar y probar las referencias de eventos. El hash del BPS nuevo debe coincidir con constantes del parcheador **antes** de compilar su variante privada. Para un EXE de interfaz sin payload: `cd patcher && GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags='-H=windowsgui -s -w' -o /tmp/cladun-interfaz.exe ./cmd/cladun-patcher`. El EXE privado requiere un BPS ignorado en `patcher/cmd/cladun-patcher/traduccion_es_experimental.bps` y `-tags cladun_embedded`, **solo tras** actualizar SHA destino/BPS y superar validaciones. Evitar subir ejecutables de prueba sin validar como releases finales.

## Entregables OBLIGATORIOS en la respuesta y en GitHub

1. Qué hiciste realmente, por qué, pasos y comandos ejecutados; IDs/archivos y prueba objetiva de causa.
2. Capturas/vídeo PPSSPP verdaderos con versiones y resolución, y pruebas regresivas; si no hay ejecución, declarar explícitamente qué falta.
3. Hashes originales/candidatos/BPS, controles de opcode, PSPFS, fuente; resultado de pruebas. Nunca afirmar seguridad de eventos únicamente por comparar bytes.
4. Rama, commits, PR y enlaces confirmados; documentación/QA del cambio; actualizar `reports/ESTADO_CONTINUIDAD_PPSSPP.json`.
5. **Guardar y entregar EL NUEVO PROMPT AUTÓNOMO** en `prompts/SIGUIENTE_TAREA.md`, incluyendo el siguiente objetivo específico, lo resuelto, lo pendiente, causa, archivos/IDs, capturas, SHA actuales, comandos, restricciones, criterios de éxito y GitHub. **El prompt nuevo deberá exigir también crear otro prompt al terminar**. Hacerlo después de CADA fase, incluso cuando haya un bloqueo.

No pidas de nuevo datos ya disponibles. No prometas trabajo diferido. Emplea las herramientas y archivos reales de esta conversación y sé exacto al distinguir validado de pendiente. El objetivo no es solo traducir el corpus: es **integración funcional y visual completa sin corromper recursos**.
