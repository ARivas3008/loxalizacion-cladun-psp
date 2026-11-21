# F1 — Experimento del menú de configuración (20/11/2026)

**Estado: auditoría estática realizada; reparación visual NO demostrada.**

## Evidencia verificada en la ISO original

Se extrajo localmente la ISO USA aportada por el usuario. Su SHA-256 es b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f y mide 305.496.064 bytes. Contiene 349 entradas PSPFS. DATABASE.DAT (PSPFS #193, IMY) se descomprimió a 620.032 bytes. STRTBL.DAT ocupa 17.744 bytes y su SHA-256 es 16d9da36c05380cbb8af7eba53cb26c7b3e21f8ef5c80fdb90fdba20621044bf. FONT.BIN original contiene 2.721 registros; SHA-256 1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46. Espacio ASCII: 7 px; espacio ideográfico: 15 px.

Las mediciones de unos 764 px (original) y 333 px (parche v0.1.5) proceden de evidencia privada PPSSPP anterior, **no repetida en esta sesión**. No se ha probado aún si la rutina de ventana utiliza el avance de las cadenas; no confundir correlación con causa.

| ID | Avance original | Español actual | Variante F1 (estática) |
| --- | ---: | ---: | ---: |
| 005695 Retro | 85 | 33 | 85 |
| 005696 Real | 83 | 59 | 83 |
| 005697 %2d | 99 | 22 | 99 |
| 005698 Correr | 170 | 106 | 170 |
| 005709 Decimales de daño | 303 | 111 | 303 |
| 005713 APAGADO | 84 | 115 | No modificada |

Los valores son sumas de avances FONT.BIN, **no** anchuras observadas en PPSSPP. Se conservan tildes y etiquetas de 005687–005694.

## Cambios implementados

La nueva herramienta **tools/experimento_menu_f1.py** lee el FONT.ARC de la ISO USA mediante el parser existente, valida el hash de la ISO, mide los caracteres por código y propone cinco alternativas de sangría/rótulo con avance igual al original. Nunca sobrescribe el corpus ni el borrador canónico: crea un CSV alternativo que el integrador ya admite con su argumento --borrador. Puede aplicarse solo a un ID con --ids. Rechaza ISO ajenas, destinos existentes, IDs fuera de alcance y cambios del marcador %2d.

**tests/test_experimento_menu_f1.py** comprueba prefijos, sufijos, anchos, rechazo de IDs y protección de marcadores. En GitHub Actions, ejecución 44861999891, commit a75bcb34954cc38483977e7550f8d40ea1305b5e, se completaron correctamente **120 tests Python**, integridad de corpus y borrador, planificación, pruebas Go y compilación pública Windows sin payload. La fuente USA se cotejó aparte en el entorno privado; el runner de CI no contiene la ISO original.

Informes cuantitativos: **reports/menu_f1_metricas_original_2026-11-20.json**. **No hay candidata ISO/BPS v0.1.6 ni capturas nuevas.** No se ha demostrado corrección del fallo.

## Experimentos reproducibles siguientes

Desde la raíz del repositorio, con los destinos vacíos y una copia privada de la ISO:

~~~bash
export ISO_ORIGINAL='/ruta/privada/Cladun_USA_original.iso'
mkdir -p /tmp/cladun-f1/{csv,reportes,iso,bps}
sha256sum "$ISO_ORIGINAL"
python -m unittest tests.test_experimento_menu_f1 -v

# Un único marcador de valor
python tools/experimento_menu_f1.py --iso "$ISO_ORIGINAL" \
  --salida-csv /tmp/cladun-f1/csv/f1-005697.csv \
  --reporte /tmp/cladun-f1/reportes/f1-005697.json --ids 005697

# Una única cadena de anchura máxima
python tools/experimento_menu_f1.py --iso "$ISO_ORIGINAL" \
  --salida-csv /tmp/cladun-f1/csv/f1-005709.csv \
  --reporte /tmp/cladun-f1/reportes/f1-005709.json --ids 005709

# Variante conjunta (comprobar después de variantes individuales)
python tools/experimento_menu_f1.py --iso "$ISO_ORIGINAL" \
  --salida-csv /tmp/cladun-f1/csv/f1-todos.csv \
  --reporte /tmp/cladun-f1/reportes/f1-todos.json
~~~

Para cada variante, cambiar NOMBRE. El integrador debe conservar la protección de eventos:

~~~bash
NOMBRE='f1-005709'
python tools/integrar_parche_seguro.py \
  --iso "$ISO_ORIGINAL" \
  --borrador "/tmp/cladun-f1/csv/$NOMBRE.csv" \
  --candidate "/tmp/cladun-f1/iso/$NOMBRE.iso" \
  --report "/tmp/cladun-f1/reportes/$NOMBRE-integracion.json" \
  --experimental-parcial --event-safe-only

python tools/generar_parche_bps.py --original "$ISO_ORIGINAL" \
  --candidato "/tmp/cladun-f1/iso/$NOMBRE.iso" \
  --informe-integracion "/tmp/cladun-f1/reportes/$NOMBRE-integracion.json" \
  --salida "/tmp/cladun-f1/bps/$NOMBRE-EXPERIMENTAL.bps" \
  --informe-bps "/tmp/cladun-f1/reportes/$NOMBRE-bps.json" \
  --experimental --event-safe-only

sha256sum "$ISO_ORIGINAL" "/tmp/cladun-f1/iso/$NOMBRE.iso" \
  "/tmp/cladun-f1/bps/$NOMBRE-EXPERIMENTAL.bps"
~~~

Comparar en **PPSSPP 1.20.4** la ISO original, v0.1.5, la variante solo 005697, solo 005709 y la conjunta, a igual resolución y con las mismas opciones/selección. Guardar capturas REALES, medidas en píxeles, cursor, valores, iconos y ayudas. Confirmar si la anchura se altera; si no, revisar DB sola, fuente sola, SYS.DAT2 solo y la función del motor que dimensiona cuadros. No usar imágenes recreadas como evidencia. El modo --sin-fuente es diagnóstico y no acredita la representación de acentos.

## Criterios para cerrar F1

1. Capturas PPSSPP de la misma pantalla original y reparada, sin solapes ni recortes y con al menos dos recorridos de cursor.
2. Determinar causalidad con ensayos aislados: no basta igualar anchos estáticos.
3. Hashes SHA-256 nuevos de ISO y BPS, roundtrip BPS, preservación de recursos PSPFS e ISO9660, y cero movimiento de offsets de los 51.705 comandos y 1.625 scripts.
4. Mantener las mejoras españolas, 19 glifos y símbolos de controles; no editar instrucciones de eventos ni otros assets.
5. Solo después de esto consolidar el texto en el CSV canónico y pasar a F2/F3.

No versionar ISO, BPS, PBP, fuentes, texturas ni ejecutables del juego. Al finalizar cada iteración, actualizar **reports/ESTADO_CONTINUIDAD_PPSSPP.json** y **prompts/SIGUIENTE_TAREA.md** con un nuevo prompt autónomo, que obligue a repetir este relevo.
