# Auditoría de menú, tildes y símbolos — Cladun ES v0.1.5 (20/11/2026)

**Estado:** revisión binaria de ISO original USA, BPS v0.1.4 y corrección privada v0.1.5. **No hay validación visual de v0.1.5 en PPSSPP.** La compilación sigue siendo **experimental y parcial** por la protección de eventos.

## 1. Configuración: cadenas comprobadas en la ISO parcheada

Se leyó directamente DATABASE.DAT/STRTBL.DAT de la ISO reconstruida y se cotejó por ID, no solo desde el CSV. **Se conservaron exactamente las mejoras del corpus**:

| ID | Antes (inglés) | En la ISO (español) |
|---|---|---|
| 005687 | SFX Volume | Vol. efectos |
| 005688 | BGM Volume | Vol. música |
| 005689 | BGM Type | Tipo música |
| 005690 | Key Config | Controles |
| 005691 | Changes volume of sound effects. | Ajusta el volumen de los efectos. |
| 005692 | Changes volume of BGM. | Ajusta el volumen de la música. |
| 005693 | Changes BGM type (Real/Retro) | Elige música real o retro. |
| 005694 | Changes button configuration. (Switches screen) | Configura los botones. |

Coincidencia binaria con la cadena codificada en el borrador español: **8 de 8**.

## 2. Tildes y signos

- El códec experimental de **19 glifos de un byte A1–B3** permanece sin sustitución ni transliteración.
- Las fuentes contienen 2.721 glifos de origen con píxeles idénticos consultados por código CP932; 19 símbolos nuevos completan 2.740 registros.
- **Fallo demostrado en v0.1.4:** la rotación de 180° de los signos ¿ (AF) y ¡ (B0) los desplazaba al extremo derecho de la celda 16×16, fuera del margen previsto por el glifo original. Eso puede superponerlos con caracteres vecinos.
- **Corrección en v0.1.5:** tras rotar se restablece el mismo margen izquierdo que el glifo base. Comprobación de píxeles: solo los códigos AF y B0 cambiaron; todos los otros 2.738 glifos son idénticos a v0.1.4.
- La tabla FONT.BIN y el tamaño de FONT.ARC quedaron intactos entre v0.1.4 y v0.1.5: **144.192 bytes**. Nada de scripts, eventos, archivos ISO9660 ni los otros 348 recursos PSPFS se cambió respecto a v0.1.4.

## 3. Símbolos de botones: riesgo real aún NO resuelto

FONT.BIN ordena los glifos por código. Al insertar 19 glifos de un byte inmediatamente después de los ASCII, **2.626 glifos originales** cambian de índice físico en el atlas (solo 95 conservan índice). Los 23 símbolos analizados, incluidos los códigos CP932 **874A–8750 (⑪–⑰)**, 819B (○), 81A2 (△), 81A0 (□) y 817E (×), conservan sus píxeles cuando se buscan *por código*. Sin embargo, todos esos índices físicos han aumentado **19 posiciones** (por ejemplo, ⑪ de 441 a 460).

Si alguna ruta del motor utiliza índices fijos del atlas en vez de consultar el código de FONT.BIN, puede mostrar un símbolo equivocado. **No se ha demostrado que el motor lo haga, ni se ha excluido.** Requiere inspección del renderizado y de las referencias internas del motor. El parche v0.1.5 **no corrige ni certifica** este riesgo. No publicar como solución total del problema de iconos.

## 4. Espaciado del menú: problemas localizados

El ancho se estimó sumando el avance almacenado en los metadatos del propio FONT.BIN (píxeles de fuente), sin afirmar que reproduce exactamente el layout del motor.

| ID | Texto original -> texto insertado | Ancho original -> parche |
|---|---|---|
| 005695 | Retro (con tres espacios ideográficos y un espacio de margen) -> Retro | **85 -> 33 px** |
| 005696 | Real (con tres espacios ideográficos y dos ASCII) -> cinco espacios y Real | **83 -> 59 px** |
| 005697 | diez espacios + %2d + espacio -> %2d | **99 -> 22 px** |
| 005698 | Run + diez espacios ideográficos -> Correr + diez ASCII | **170 -> 106 px** |
| 005709 | Show decimal points for damage + espaciado -> Decimales de daño | **303 -> 111 px** |
| 005713 | nueve espacios + OFF -> nueve espacios + APAGADO | **84 -> 115 px** |

Estos son **desajustes mensurables de avance y pérdida de sangrías**, aunque no prueban por sí mismos un error visual. También merece revisarse la opción 005710, cuyo original «ON» aparece actualmente como «EN». Las mejoras de redacción se mantienen en CSV y en ISO, pero no se ha certificado su correcta alineación en todas las pantallas.

**No se modificaron automáticamente los textos del menú ni sus sangrías** en v0.1.5 porque esas cadenas pueden usarse en más de un diseño; antes de un parche correctivo de layout, deben comprobarse en su pantalla real. Así se evita introducir ajustes que arreglen un contexto y rompan otro.

## 5. Integridad de v0.1.5

- ISO original exacta SHA-256: `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- ISO candidata v0.1.4 SHA-256: `7d7d598c719500deaf58cb8535106396745221da16f39ee9e3a2530f92da9fc8`.
- ISO candidata v0.1.5 SHA-256: `9be7b07a2c5c8c9026ffd0f829f613237f9a31e8fe2455856649ff6c1fe2b4ef`.
- BPS v0.1.5 SHA-256: `976fda78adf3e6c2c3c31d5b89bc2f04b18c0905789305b25e9d0a58bf8cea0c`.
- EXE v0.1.5 SHA-256: `82d33e51277a7fb3eaecc522bad89cb2f5974a65a81d1c81ed5c5e5d55d89606`.
- Reconstrucción por BPS desde la ISO original: SHA-256 de candidata exacto; recursos PSPFS e ISO9660 ajenos cotejados byte a byte.
- Eventos: se conserva el modo v0.1.4 que no desplaza comandos, con 4.524 traducciones de script pospuestas; ningún comando de eventos se tocó en este hotfix.

**No representa una validación PPSSPP, ni corrige la visualización de todos los símbolos.** La actualización se deja en el PR experimental como candidato de comprobación.
