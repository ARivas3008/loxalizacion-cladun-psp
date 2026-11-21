# NUEVA TAREA AUTÓNOMA CLADUN ES — F1: ejecutar PPSSPP REAL y aprobar ancho/ON–OFF

Actúa como especialista PSP/PPSSPP 1.20.4, ingeniería inversa, CSV/CP932, eventos, ISO9660, DSARC, PSPFS, BPS y validación funcional. **Debes ejecutar cambios y pruebas reales**, preservar recursos comerciales privados y actualizar GitHub. No confundas una auditoría de la ISO original con una auditoría de ISO candidata, ni ejecuciones CI con evidencia visual. Mantén F1 **ABIERTA** hasta que la prueba en PPSSPP y la integridad de la candidata estén demostradas.

## 1. Repositorio, rama y archivos de lectura previa

GitHub: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: `integracion-eventos-segura-20261120`
PR borrador #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base: `revision-manual-dialogos`
Último commit de código comprobado: `3c6276dc7f13974fbd085510c96e91cff53c1f3c`. Consultar HEAD actual antes de escribir.

Lee **antes de cambiar**: `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-20.md`, `docs/EXPERIMENTO_MENU_F1_2026-11-20.md`, `docs/RESULTADO_F1_SESION_2026-11-21.md`, `reports/RESULTADOS_F1_PPSSPP_REAL_2026-11-20.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `reports/auditoria_original_f1_2026-11-21.json`, `reports/metricas_menu_f1_2026-11-21.json`, `tools/menu_layout_es.py`, `tools/experimento_menu_f1.py`, `tools/experimento_menu_f1_residuo.py`, `tools/experimento_onoff_f1.py`, `tools/auditar_f1_fuente_original.py`, `tools/integrar_parche_seguro.py`, `tools/generar_parche_bps.py`, `tests/test_menu_layout_es.py`, `tests/test_experimento_menu_f1_residuo.py`, `tests/test_experimento_onoff_f1.py`.

## 2. Historia comprobada y hashes (no atribuir nuevas pruebas a sesiones anteriores)

ISO USA privada original: **305.496.064 bytes**, SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. El 21/11/2026 se auditó nuevamente desde el archivo 7z aportado por el usuario, con resultado real: 16 registros ISO9660 (12 archivos), `DATA.DAT` offset 113.770.496 tamaño 191.697.408, SHA-256 `7f4db811e5d079ed58c15ee21cc14ab472d58d93f5c97378982a922c39af3404`; 349 PSPFS únicos; DSARC DATABASE 30, FONT 7 y SCRIPT 4 miembros; `SCRIPT.DAT`: **51.705 comandos**, 46.308 no textuales, 5.397 textuales y 1.625 scripts. **Esta auditoría es del ORIGINAL, no de ISO candidata**. STRTBL.DAT original SHA `16d9da36c05380cbb8af7eba53cb26c7b3e21f8ef5c80fdb90fdba20621044bf`, FONT.BIN original SHA `1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46`.

**20/11/2026, PPSSPP real histórico** 1.20.4 Linux Xvfb 1280×720×24, ventana 960×544+160+88, software renderer, SDL_AUDIODRIVER=dummy, navegación Return → Down → z:
- USA original: **756 px interior / ≈764 exterior**, x342..1097.
- v0.1.5: **324 / ≈332**, x774..1097, solapes.
- Solo 005697: **324 / ≈332**, negativo.
- Solo 005709 corregido: **740 / ≈748**, x358..1097, sin solapes observados en Opciones; apertura de Controles.
- Cinco cambios de espacios: **740 / ≈748**.
Método de PNG real: fila y=106, segmento claro con R,G,B>125 en x=160..1104; exterior ≈ interior+8 px. ZIP privado `Cladun_F1_capturas_reales_PPSSPP_2026-11-20.zip`, SHA `4d7f83259dcfe37242700c6cce1dbbee9e36945c1860d5e9fff9a30c7b58cae2` **NO SUBIR**.

La causa aislada de la contracción es eliminar relleno ideográfico de **005709** en DATABASE.DAT/STRTBL.DAT. El integrador canónico lo restituye SOLO para CSV canónicos, con `tools/menu_layout_es.py`: «Decimales de daño» + 10 U+3000 + 6 espacios ASCII, sin tocar el borrador literario. Si usas `--borrador` externo, el override **NO** se ejecuta; la herramienta nueva incorpora el relleno explícitamente.

Hash ISO canónica F1 ya probada visualmente: `9b7fc809bb106953a91d6ad6e4e23363eb7fb92760659607d484f71132b5da89`; BPS de la misma: `5047fa7b565f84ec204f7f1dde4e47752eb2013af8daa40d68714ca7255b1566`.
Hash ISO variante experimental **+1 U+3000 NO PROBADA VISUALMENTE**: `f97fa355fce8d7ab55a81fc711e944185ebdce4a320a5077695cb445acd303c8`; BPS `279bd99d7a0cfb87fd1bb4a03ee67ecc250d51563e14f12e213283922a8634fc`.

Métricas del FONT.BIN original, NO PPSSPP: 005709 original=303 px, borrador=111, mínimo corregido=303, +1 ideográfico=318; 005710 original «          ON»=84, borrador «          EN»=84, candidato «          Sí»=80; 005713 original «         OFF»=84, borrador «         APAGADO»=115, candidato «         No»=77. 005711 original «　Under 1 ON»/borrador «Menos de 1: SÍ» y 005712 « Under 10 ON»/borrador «Menos de 10: SÍ» son opciones asociadas; preservarlas en ensayos aislados. El relleno +15 px no demuestra automáticamente +16 px en la caja; evaluar redondeo.

El 21/11/2026 se añadieron `tools/experimento_menu_f1_residuo.py`, `tests/test_experimento_menu_f1_residuo.py`, `tools/auditar_f1_fuente_original.py` y un reporte sin activos. CI para commit `3c6276dc...`: runs **44905002958** y **44904998228**, ambas SUCCESS: **134 pruebas Python**, Go, integridad y build Windows SIN payload. **NO** se descargó PPSSPP en esa sesión (fallo DNS), **NO** se construyeron nueva ISO/BPS, **NO** hubo capturas nuevas ni QA funcional. El CSV maestro y sus TXT siguen intactos; F1 ABIERTA.

## 3. Próximo trabajo concreto obligatorio

**P0 — Ensayo exacto +1 U+3000.** Recupera PPSSPP 1.20.4 oficial desde:
https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
SHA-256 exacto `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. No uses otro binario sin reportarlo. Reconstruye el CSV aislado **solo 005709** con `tools/experimento_menu_f1_residuo.py`. Integra con `--borrador`, `--experimental-parcial`, `--event-safe-only`; **comprueba que la ISO coincide exactamente con f97fa...03c8 antes de PPSSPP**; ante diferencia, detener, auditar y conservar la corrección mínima existente. Genera BPS privado con roundtrip y coteja hash. Arranca en PPSSPP real, navega Opciones con Return/Down/z, captura PNG original/canónica/+1 y mide fila y=106, compara anchos, bordes, ayudas, posición y ausencia de recortes. Si +1 no recupera ≈764 o introduce regresiones, no lo adoptes; investigar rutinas de tamaño/redondeo de ventanas del motor.

**P0 — Valores ON/OFF.** Usa `tools/experimento_onoff_f1.py` para candidatos **aislados** de 005710 y 005713 y su combinación (incorpora corrección mínima 005709 aun para `--borrador`). Ensayar «Sí/No» frente a fuente original, sin olvidar los modos 005711–12 y sus traducciones. Cotejar anchor, sangría, márgenes y símbolos de valores en cada estado PPSSPP. No adoptar por traducción lingüística sin prueba visual. Si apruebas cambio literario, actualizar CSV canónico, **ambos TXT**, bitácora antes/después y vistas derivadas en el mismo commit, preservando offsets/IDs/variables. Espacios de presentación separados del contenido.

**P0 — Recorrido F1 completo.** Ensayar todos los cursores de Opciones, volumen efectos/música, Real/Retro, decimales, círculo mágico, capturas, Controles, cambio de valores y regreso al menú. Tomar **al menos dos PNG reales por pantalla**, guardar hashes PNG y controlar títulos, ayudas, iconos L/R, cuadrado, círculo, cruz y triángulo. **NO** cerrar F2 sin probar acceso por código frente a índice de atlas desplazado +19 por glifos A1–B3.

**P0 — Integridad NUEVA candidata.** Auditar 349 PSPFS (345 ajenos a cuatro contenedores textuales intactos), DSARC, ISO9660 ajenos, 51.705 comandos y 46.308 no textuales, 1.625 scripts, cero desplazamientos, y **4.524 traducciones aplazadas**. BPS roundtrip y SHA-256 exactos. No eliminar `--event-safe-only`. Dejar F1 abierta si falla alguna prueba. Nunca subir ISO, BPS, EBOOT, FONT ni capturas comerciales a GitHub.

## 4. Comandos reproducibles (salidas deben ser NUEVAS)

```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f1-preflight-actual.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f1-integrabilidad-actual.json
(cd patcher && go test ./...)
git diff --check

export ISO_ORIGINAL='/ruta/privada/Cladun_USA_original.iso'
export SALIDA='/ruta/privada/f1-reintento-ppsspp'
mkdir -p "$SALIDA"
sha256sum "$ISO_ORIGINAL"
python tools/auditar_f1_fuente_original.py --iso "$ISO_ORIGINAL" --reporte "$SALIDA/original.json"

# CSV aislado: solamente 005709 pasa a español + 10 U+3000 + 6 ASCII + 1 U+3000.
python tools/experimento_menu_f1_residuo.py --iso "$ISO_ORIGINAL" --salida-csv "$SALIDA/extra.csv" --reporte "$SALIDA/extra-csv.json"
python tools/integrar_parche_seguro.py --iso "$ISO_ORIGINAL" --borrador "$SALIDA/extra.csv" --candidate "$SALIDA/extra.iso" --report "$SALIDA/extra-integracion.json" --experimental-parcial --event-safe-only

python - "$SALIDA/extra.iso" <<'PY'
import hashlib,sys
path=sys.argv[1]
with open(path,'rb') as f:
    h=hashlib.sha256()
    for chunk in iter(lambda:f.read(1<<20),b''):
        h.update(chunk)
assert h.hexdigest()=='f97fa355fce8d7ab55a81fc711e944185ebdce4a320a5077695cb445acd303c8', 'STOP: SHA inesperado, NO PPSSPP ni BPS'
print('SHA ISO extra PASS')
PY

python tools/generar_parche_bps.py --original "$ISO_ORIGINAL" --candidato "$SALIDA/extra.iso" --informe-integracion "$SALIDA/extra-integracion.json" --salida "$SALIDA/extra.bps" --informe-bps "$SALIDA/extra-bps.json" --experimental --event-safe-only
sha256sum "$ISO_ORIGINAL" "$SALIDA/extra.iso" "$SALIDA/extra.bps"

# Separar variantes ON, OFF y ON+OFF con destinos CSV/JSON/ISO/BPS inéditos.
python tools/experimento_onoff_f1.py --iso "$ISO_ORIGINAL" --modo si-no --ids 005710 --salida-csv "$SALIDA/on.csv" --reporte "$SALIDA/on.json"
python tools/experimento_onoff_f1.py --iso "$ISO_ORIGINAL" --modo si-no --ids 005713 --salida-csv "$SALIDA/off.csv" --reporte "$SALIDA/off.json"
python tools/experimento_onoff_f1.py --iso "$ISO_ORIGINAL" --modo si-no --salida-csv "$SALIDA/onoff.csv" --reporte "$SALIDA/onoff.json"
```

Repetir integración/BPS privado para cada variante ON/OFF, validar SHA nuevos y todos los invariantes. PPSSPP y capturas deben mostrar dos estados por pantalla; una foto recreada no vale. Si no es posible ejecutar emulador, documentar el bloqueo y los comandos; nunca decir que F1 está cerrada.

## 5. Fases futuras y RELEVO RECURSIVO OBLIGATORIO

F2: glifos A1–B3, atlas desplazado +19, iconos y ¿¡; F3: intro con inglés; F4: 4.524 scripts aplazados y referencias del intérprete; F5: niveles/combate/inventario/enciclopedia/guardado/carga; F6: BPS final, EXE privado Windows y QA total. No saltar F1 bloqueada.

**AL CERRAR ESTA TAREA**: documentar SOLO hechos ejecutados, hashes y logs, screenshots PPSSPP reales con rutas privadas, integridad binaria vs validación visual/funcional, cambios y CI del HEAD, commit/PR/bloqueos. Actualizar obligatoriamente `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, informe de F1 y **REGNERAR UN NUEVO PROMPT COMPLETO AUTÓNOMO en `prompts/SIGUIENTE_TAREA.md` y mostrarlo al usuario**. El nuevo prompt deberá exigir que, al cerrar su propia ejecución, regenere otro prompt autónomo. Esta obligación se repite hasta implementar y probar la localización española completa.
