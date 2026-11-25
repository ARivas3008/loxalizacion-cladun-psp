# R36 — Perfil único de integración 7093

La ruta principal `tools/integrar_parche_seguro.py --perfil-unificado` incorpora F1, 3724 base, 146 exactos, 1302 rellenos y 1921 ligaduras deduplicadas: 7093 cambios, 3745 en SCRIPT.DAT y 3348 fuera de SCRIPT. Pendientes 1155. La fuente compacta 19+44 conserva los 2721 glifos originales; su alineación DSARC de 16 bytes sigue experimental.

## Compilación privada, una sola pasada
```bash
python tools/integrar_parche_seguro.py --iso /PRIVADO/USA.iso --candidate /PRIVADO/R36_7093.iso --report /PRIVADO/R36_7093.json --perfil-unificado
```
La opción activa offsets fijos, corpus canónico, fuente y modo parcial. Rechaza rutas de salida existentes, preimágenes desconocidas, solapamientos, discrepancias frente al plan R35 y errores de fuente. SCRIPT se reconstruye una sola vez y el IMY se recomprime selectivamente. Las tres entradas DSARC ajenas permanecen iguales; se usa el verificador de eventos y el inserter PSPFS append-only. No publicar ISO ni BPS propietario.

## Evidencia
R35 CI 45544501058 SUCCESS. La evidencia A/B previa por lote no equivale a C. Las nuevas pruebas R36 comparan los 7093 IDs únicos, los 3745 cambios SCRIPT con el plan R35 independiente, la conservación de F1/R34 y el rechazo de entradas no diferidas. No se ha construido la ISO acumulada R36 localmente (checkout bloqueado por DNS), ni ejecutado PPSSPP. Perfil histórico 3724 permanece sin cambios; perfil unificado experimental 7093/8248 = 85,99%. No declarar release. Próximo: ejecutar la candidata privada y clasificar los 1155 pendientes en lotes 1000 + 155.
