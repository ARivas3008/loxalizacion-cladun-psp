# F1: instrumento de medición PNG y variante ON/OFF con margen (21/11/2026)

## Código incorporado

- `tools/medir_f1_ppsspp.py` analiza **capturas PNG proporcionadas**, verificando firma y tamaño exacto 1280×720, hash SHA-256 por archivo, y fila y=106 con umbral R,G,B>125, x=160..1104. Para la pantalla «Opciones» devuelve segmento interior y anchura exterior **estimada**, sin generar ni alterar imágenes.
- `--exigir-dos-estados` requiere al menos dos estados únicos de cada pantalla y versión registrada. **No confirma que el PNG provenga de PPSSPP**: el informe lo declara expresamente.
- `tests/test_medir_f1_ppsspp.py` prueba el algoritmo con fixtures sintéticos **solo en memoria o temp**; no son ni se publican como capturas reales.
- `tools/experimento_onoff_f1.py`: nuevo modo privado `--modo si-no-espacio-final` con `005710 = "          Sí"`, `005713 = "         No "`; en FONT.BIN original la segunda cadena aumenta de **77 a 84 px de avance**, lo mismo que el inglés «         OFF» de 84 px. **No se aprueba visualmente**, y no se cambia ningún CSV/TXT canónico. ID 005709 conserva override mínimo y 005711–12 permanecen intactos.

## Límite de la sesión

El archivo 7z privado se extrajo de nuevo; ISO USA SHA-256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f (305496064 bytes). Se ejecutó independiente auditoría read-only: 349 PSPFS; 30/7/4 miembros DSARC DATABASE/FONT/SCRIPT; 1625 scripts; 51705 comandos y 46308 no textuales. Los hashes de STRTBL.DAT y FONT.BIN fueron idénticos a los esperados. Informe privado `auditoria_esta_sesion.json`, no contiene recursos del juego.

Este entorno **no contiene PPSSPP y no resuelve github.com** al intentar descargarlo; no se capturó ninguna pantalla real y no se regeneró ISO/BPS F1 desde el integrador completo. No declarar 764 px corregidos ni F1 cerrada hasta disponer de captura PPSSPP real, ISO/BPS del mismo candidato y QA de cursor/ayudas/controles.

## Formato de manifiesto privado para medir

```json
{
  "schema": "cladun.f1.ppsspp_png_inputs.v1",
  "origen": "PPSSPP real 1.20.4, version y captura registradas por el operador",
  "capturas": [
    {"ruta": "/privado/opciones_original_estado1.png", "pantalla": "Opciones", "version": "USA", "estado": "opcion-1"},
    {"ruta": "/privado/opciones_original_estado2.png", "pantalla": "Opciones", "version": "USA", "estado": "opcion-2"}
  ]
}
```

Añadir a este ejemplo todas las variantes y pantallas requeridas, con `sha256_esperado` por PNG si ya se registró externamente. No subir manifiestos con rutas privadas ni capturas comerciales a GitHub.

```bash
python tools/medir_f1_ppsspp.py --manifiesto /privado/f1/capturas.json --reporte /privado/f1/medidas.json --exigir-dos-estados
```

Estas herramientas son auxiliares; **la ejecución visual real continúa pendiente**.
