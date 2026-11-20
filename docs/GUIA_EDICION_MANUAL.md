# Guía para corregir textos y nombres de hablante - Cladun PSP

**Proyecto:** Cladun: This Is an RPG! USA/PSP. **Rama:** `revision-manual-dialogos`.  
**Carácter del material:** corpus de revisión, no garantía de inserción ni de funcionamiento completo en PPSSPP.  
**Norma principal:** editar **solo** la columna `espanol` de `traduccion/CLADUN_BORRADOR_ES.csv`. El archivo original, IDs, offsets y bytes originales deben conservarse.

## 1. Qué muestra la captura y cuál es el problema

En la captura aparecen espacios anormales: `Joven frené tico`, `sin má s`, `¿Está s cansado?`, `¡Mi raté!`. Sin embargo, en el CSV se encuentran `Joven frenético`, `¡No te vayas así sin más!`, `¿Estás cansado? ¿Te duele algo?` y `¡Mírate! ¡Estás cubierto de barro!`, correctamente escritos. **Es un indicio de problema de renderizado, espaciado o anchura de la fuente**, no una demostración de que las frases estén mal escritas en el CSV. Debe investigarse la implementación de glifos personalizados `F5A0-F5B2`, su avance horizontal y el tamaño de los cuadros.

Las traducciones también pueden tener problemas de naturalidad o sentido independiente del renderizado. Por ejemplo, `Your mom and dad asked me to look after you.` fue convertido a `Me pediste que te cuidara.` y **cambia quién realizó la petición**. Es una corrección textual auténtica a revisar en contexto.

## 2. Herramientas recomendadas

| Herramienta | Para qué sirve | Instalación |
| --- | --- | --- |
| `editor/Cladun_Editor_Offline.html` | Buscar por ID, nombre, escena y original; editar solo español; exportar CSV | Ninguna: abrir en navegador moderno |
| VS Code (opcional) | Comparación de versiones y búsqueda en archivos | Opcional, para revisión avanzada |
| `lectura/CLADUN_GUION_CON_HABLANTES_ES.txt` | Leer diálogos con etiquetas de interlocutor y originales, por escena | Ninguna |
| `traduccion/CLADUN_BORRADOR_ES.csv` | Fuente editable real | Viene con el repositorio |
| `traduccion/GLOSARIO_CANONICO.csv` | Terminología canónica | Viene con el repositorio |
| Python 3.10+ (para mantenedor) | Validar y sincronizar cambios en el repositorio | Solo quien prepara el parche |
| PPSSPP (pruebas) | Comprobar el texto y las ventanas dentro del juego | Emulador separado |

No se necesita Photoshop, un editor hexadecimal ni modificar la ISO para corregir una frase. No uses procesadores de texto que cambien la codificación o añadan comillas automáticamente.

## 3. Edición de un diálogo, paso a paso

1. Descarga la rama `revision-manual-dialogos` de GitHub o clónala. Haz una copia de seguridad del CSV.
2. Abre `editor/Cladun_Editor_Offline.html` con doble clic. Pulsa el selector de archivo y abre **`traduccion/CLADUN_BORRADOR_ES.csv`**. El navegador mantiene el contenido local.
3. Busca el `text_id` de la entrada o una frase. Ejemplo real: el nombre `Joven frenético` es grupo `000784` / `CLD-000803`; sus tres diálogos son grupos `000785-000787`.
4. Comprueba el **texto original** y, cuando exista, el **hablante**. Corrige únicamente la caja **Español**. Preserva signos, variables y contenido; no inventes frases.
5. Pulsa **Guardar cambio en memoria**. Puedes seguir corrigiendo más entradas.
6. Pulsa **Exportar CSV corregido**. Obtendrás `CLADUN_BORRADOR_ES_CORREGIDO.csv`. No cambies a mano los identificadores, offsets, fuentes o bytes.
7. En una terminal, desde la raíz del repositorio, valida el archivo sin escribir nada:

   ```powershell
   python tools/aplicar_correcciones_editor.py --entrada "C:\Ruta\CLADUN_BORRADOR_ES_CORREGIDO.csv"
   ```

8. Si no hay errores, sincroniza CSV, los dos TXT heredados, la lectura por personaje y la bitácora:

   ```powershell
   python tools/aplicar_correcciones_editor.py --entrada "C:\Ruta\CLADUN_BORRADOR_ES_CORREGIDO.csv" --aplicar
   ```

   El programa guarda respaldos locales en `.local/backups/` (nunca subirlos a GitHub). Si falla un marcador o una columna protegida, **rechaza todo el lote**.
9. Ejecuta la validación de la rama:

   ```powershell
   python tools/verificar_borrador_es.py
   python tools/verificar_integridad.py --raiz .
   python -m unittest discover -s tests -v
   python tools/auditar_preinsercion_es.py --reporte reports/revision_manual.json --filas reports/revision_manual.csv
   python tools/reportar_integrabilidad_es.py --reporte reports/integrabilidad_manual.json
   ```

10. Haz un commit de los archivos de texto modificados y registra el ID o escena corregida. **No subas ISO, recursos comerciales ni binarios.**

## 4. Cómo está construido el guion con hablantes

El extractor del juego identifica tres tipos de campos de SCRIPT.DAT: `0x66` para diálogo, `0x69` para opción y **`0x6E` para el nombre mostrado al hablar**. La vista `lectura/CLADUN_GUION_CON_HABLANTES_ES.txt` incluye una escena, el nombre identificado y la traducción junto al original, con los IDs.

Ejemplo real en `demo1001_00.dsf` / `script_id = 100100`:

```text
[NOMBRE DE PANTALLA 0x6E] Joven frenético
  id=CLD-000803 | original: Frantic Young Man
[Joven frenético] [ID CLD-000804 | grupo 000785 | orden 193]
  ES: ¡No te vayas así sin más!
  EN: Don't just run off like that!
[Joven frenético] [ID CLD-000805 | grupo 000786 | orden 194]
  ES: ¿Estás cansado? ¿Te duele algo?
  EN: Are you tired? Are you hurt?
[Joven frenético] [ID CLD-000806 | grupo 000787 | orden 195]
  ES: ¡Mírate! ¡Estás cubierto de barro!
  EN: Look at you! You're covered in mud!
[HABLANTE NO VERIFICADO] [ID CLD-000807 | grupo 000788 | orden 206]
  ES: Te dije que no me siguieras,
  EN: I told you not to follow me,
```

**Límite importante:** cuando el motor cambia de voz mediante otros comandos, no necesariamente hay un nuevo `0x6E`. El generador asigna el primer bloque de líneas inmediatamente posterior al nombre y continuidad corta (diferencias de orden 1 o 2) como **atribución probable**, y reinicia la voz después de saltos o cambios de escena. Por tanto, `HABLANTE NO VERIFICADO` significa que la identidad debe cotejarse en PPSSPP. La vista **no inventa nombres ni convierte una hipótesis en hecho**.

`lectura/CLADUN_LECTURA_TOTAL_CON_HABLANTES_ES.txt` contiene, además del guion, todos los otros elementos textuales. Ambos archivos son **de consulta**, no formato de edición ni de reinserción.

## 5. Diagnóstico de texto cortado o separado

Antes de reescribir frases, compara el CSV con la pantalla:

- Si `espanol` ya está bien escrito, comprueba glifos (`á`, `é`, `í`, `ó`, `ú`, `ñ`, `¿`, `¡`), métricas de la fuente, salto automático y ancho del cuadro.
- En el prototipo, 19 caracteres españoles usan códigos privados `F5A0-F5B2` en `tools/charset_es.py`. Su codificación puede ser reversible y aun así dibujar con ancho incorrecto.
- Comprueba los nombres de personaje en la caja pequeña y los diálogos en la caja grande: pueden necesitar límites diferentes.
- Una abreviación breve puede ayudar a una ventana estrecha, **pero no soluciona una métrica de glifo defectuosa**. Ejemplo posible sujeto a revisión: `Joven nervioso` en vez de `Joven frenético`; no sustituir sin valorar el significado.
- Revisa ambas capturas en PPSSPP y un segundo punto del juego antes de confirmar. Si hay caracteres desplazados a mitad de palabra con el CSV correcto, registra una incidencia gráfica/tipográfica, no una corrección de traducción.

No elimines tildes o signos de apertura como solución definitiva; no cambies `bytes_hex`, `offset_hex`, `script_id` o `orden_script`.

## 6. Limitaciones y control de calidad

Los datos de trabajo tienen **9.237** unidades, de las cuales **5.207** corresponden a SCRIPT.DAT: **4.694** diálogos, **400** campos de nombre y **113** opciones. Otros **4.030** registros son menús, objetos, mapas, créditos, etc. Aunque el integrador planifique todos los textos, la traducción no está completamente revisada ni se ha probado toda la aventura en PPSSPP.

Comprueba: corrección de sentido (quién habla y a quién se dirige), nombres propios y glosario, longitud visible, signos de apertura, variables, marcadores del motor, edición única del campo `espanol`, y que el parche final no altere sprites, retratos o tiles. Repite la revisión desde la ISO original al probar un parche nuevo.

## 7. Cómo actualizar el guion después de editar

El comando `--aplicar` sincroniza las lecturas automáticamente. Para regenerarlas sin editar el CSV:

```powershell
python tools/generar_guion_hablantes.py
```

El generador además crea `lectura/CLADUN_AUDITORIA_HABLANTES.csv` y `lectura/CLADUN_RESUMEN_HABLANTES.json`. Los archivos se derivan de las posiciones fuente; el TXT de guion no debe usarse como fuente de verdad para la reinserción.

**Publicación:** la rama es de **revisión textual**, no de distribución de ISO. Mantén los experimentos de emulador y los parches jugables sujetos a pruebas independientes. No publiques una nueva versión solo porque pase el reporte binario.
