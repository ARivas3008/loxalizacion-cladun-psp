#!/usr/bin/env python3
"""F2: cotejar capturas A/B privadas del depurador PPSSPP, SIN certificar gameplay.

Este lector no produce ni fabrica capturas: abre dos manifiestos generados por
f2_ppsspp_ws_1204.py y sus PNG, compara dos pares de cuadros y verifica hashes.
Detecta *candidatos* a tinta magenta. Un resultado negativo NO prueba que
TUIKA_MES.IMY no se utilice; una captura aislada no establece MIPS/GE/VRAM.
Los hashes de las ISOs se comprueban en disco, pero ello no demuestra qué ISO
se cargó realmente en el emulador: esa identidad requiere evidencia aparte.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

USA_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
PROBE_SHA = 'b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa'
ISO_SIZE = 305496064
MANIFEST_SCHEMA = 'cladun.f2.ppsspp_private_v1204.v1'
MAX_IMAGE_BYTES = 50 * 1024 * 1024
MAX_PIXELS = 4096 * 4096
HEX_SHA = re.compile(r'^[0-9a-f]{64}$')


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def private_path(path: Path, repo: Path, *, for_output: bool = False) -> Path:
    path = Path(path).expanduser()
    if not path.is_absolute() or path.is_symlink():
        raise ValueError('Se requiere ruta absoluta privada, sin symlink')
    resolved, root = path.resolve(strict=False), repo.resolve()
    if resolved == root or root in resolved.parents:
        raise ValueError('Prohibida evidencia comercial dentro del checkout')
    if any((parent / '.git').exists() for parent in (resolved.parent, *resolved.parents)):
        raise ValueError('Prohibida evidencia en cualquier repositorio Git')
    if for_output and (resolved.exists() or path.suffix.lower() != '.json'):
        raise ValueError('Informe privado debe ser .json nuevo, sin overwrite')
    if not for_output and not resolved.is_file():
        raise FileNotFoundError(resolved)
    return resolved


def _read_png(png: Path, declared: dict) -> Image.Image:
    if png.is_symlink() or not png.is_file() or png.suffix.lower() != '.png':
        raise ValueError('PNG ausente, symlink o con extensión incorrecta')
    size = png.stat().st_size
    if size < 24 or size > MAX_IMAGE_BYTES or declared.get('bytes') != size:
        raise ValueError('Longitud de PNG no válida/coincidente')
    digest = declared.get('sha256')
    if not isinstance(digest, str) or not HEX_SHA.fullmatch(digest) or file_sha(png) != digest:
        raise ValueError('Hash SHA-256 PNG no coincide con manifiesto')
    with Image.open(png) as img:
        if img.format != 'PNG' or img.width * img.height > MAX_PIXELS:
            raise ValueError('PNG inválido o demasiado grande')
        if img.width != declared.get('psp_framebuffer_width') or img.height != declared.get('psp_framebuffer_height'):
            raise ValueError('Medidas del framebuffer declaradas incorrectas')
        img.load()  # Descarta datos truncados antes de comparar
        return img.convert('RGB')


def load_capture(manifest_path: Path, repo: Path) -> dict:
    src = private_path(manifest_path, repo)
    with src.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if data.get('schema') != MANIFEST_SCHEMA or not str(data.get('ppsspp', '')).startswith('v1.20.4'):
        raise ValueError('Manifest no acredita protocolo declarado v1.20.4')
    if 'cladun' not in str(data.get('game', {}).get('title', '')).lower():
        raise ValueError('Manifest de juego distinto')
    scene = data.get('scene')
    if not isinstance(scene, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,48}', scene):
        raise ValueError('Identificador de escena inválido')
    cap = data.get('captures')
    if not isinstance(cap, dict) or cap.get('source') != 'gpu.buffer.screenshot on paused PSP emulator (not desktop window)':
        raise ValueError('El manifiesto no declara captura del debugger PPSSPP')
    shots = cap.get('screenshots')
    if not isinstance(shots, list) or len(shots) != 2:
        raise ValueError('Se requieren exactamente dos PNG por versión')
    frames = []
    times = []
    for i, shot in enumerate(shots, start=1):
        name = shot.get('name')
        if name != f'{scene}_{i:02d}.png':
            raise ValueError('Nombre de captura inesperado o inseguro')
        path = src.parent / name
        image = _read_png(path, shot)
        frames.append(image)
        times.append(shot.get('emulated_ticks_at_pause'))
    independent_times = all(isinstance(t, (int, float)) and not isinstance(t, bool) for t in times) and times[1] > times[0]
    return {'manifest_sha256': file_sha(src), 'scene': scene, 'version': data['ppsspp'],
            'game_title': data['game']['title'], 'frames': frames,
            'capture_times_advance': independent_times,
            'dimensions': [list(f.size) for f in frames]}


def magenta(color: tuple[int, int, int]) -> bool:
    return color[0] >= 230 and color[1] <= 45 and color[2] >= 220


def compare_pair(before: Image.Image, after: Image.Image) -> dict:
    """Comparación exacta y candidatos de marcador; no interpreta su causa."""
    if before.size != after.size or before.mode != 'RGB' or after.mode != 'RGB':
        raise ValueError('Frames A/B incompatibles: tamaño o modo')
    width, height = before.size
    if width * height > MAX_PIXELS:
        raise ValueError('Frame excede límite')
    changed = new_magenta = 0
    changed_bbox = magenta_bbox = None
    def include(box, x, y):
        if box is None:
            return [x, y, x, y]
        return [min(box[0], x), min(box[1], y), max(box[2], x), max(box[3], y)]
    # PIL usa orden fila/columna, sin filtros ni reescalados que inventen diferencias.
    pix_a, pix_b = before.load(), after.load()
    for y in range(height):
        for x in range(width):
            color_a, color_b = pix_a[x, y], pix_b[x, y]
            if color_a != color_b:
                changed += 1
                changed_bbox = include(changed_bbox, x, y)
                if not magenta(color_a) and magenta(color_b):
                    new_magenta += 1
                    magenta_bbox = include(magenta_bbox, x, y)
    total = width * height
    return {'dimensions_px': [width, height], 'pixel_count': total,
            'different_pixels': changed, 'unchanged_pixels': total - changed,
            'unchanged_fraction': round((total - changed) / total, 6),
            'candidate_new_magenta_pixels': new_magenta,
            'difference_bbox_inclusive': changed_bbox,
            'candidate_magenta_bbox_inclusive': magenta_bbox,
            'zero_magenta_does_not_disprove_texture_usage': True,
            'manual_scene_alignment_required': True}


def audit(usa_manifest: Path, probe_manifest: Path, usa_iso: Path, probe_iso: Path,
          output: Path, repo: Path) -> dict:
    output = private_path(output, repo, for_output=True)
    usa_iso, probe_iso = private_path(usa_iso, repo), private_path(probe_iso, repo)
    if usa_iso.resolve() == probe_iso.resolve():
        raise ValueError('Control y sonda ISO deben ser rutas diferentes')
    hashes = []
    for path, expected in ((usa_iso, USA_SHA), (probe_iso, PROBE_SHA)):
        if path.stat().st_size != ISO_SIZE or file_sha(path) != expected:
            raise ValueError('ISO de entrada no coincide con SHA/size exigidos')
        hashes.append(expected)
    a = load_capture(usa_manifest, repo)
    b = load_capture(probe_manifest, repo)
    if Path(usa_manifest).resolve().parent == Path(probe_manifest).resolve().parent:
        raise ValueError('Capturas A/B no pueden compartir directorio')
    if a['scene'] != b['scene'] or a['version'] != b['version'] or a['game_title'] != b['game_title']:
        raise ValueError('Versiones, escenas o título del juego no coinciden')
    result = {'schema': 'cladun.f2.tuika_ppsspp_ab_metadata.v1',
              'scope': 'COMPARACION_ARCHIVOS_PRIVADOS_NO_AUTENTICA_JUEGO_POR_SI_SOLA',
              'scene': a['scene'], 'ppsspp_declared': a['version'],
              'isos_sha256_verified_from_disk': {'original': hashes[0], 'probe': hashes[1]},
              'manifest_sha256': {'original': a['manifest_sha256'], 'probe': b['manifest_sha256']},
              'capture_times_advance': {'original': a['capture_times_advance'],
                                        'probe': b['capture_times_advance']},
              'pairs': [compare_pair(x, y) for x, y in zip(a['frames'], b['frames'])],
              'frame_alignment_verified': False,
              'runtime_loaded_iso_identity_proven': False,
              'tuika_texture_runtime_origin_proven': False,
              'mips_ram_ge_vram_pipeline_proven': False,
              'f1_x11_960x544_window_regression_proven': False,
              'graphics_or_png_embedded_in_report': False,
              'warning': ('Candidatos magenta requieren cotejo manual de misma escena y origen GPU. '
                          'Cero cambios no descarta uso de TUIKA; hashes de ISO en disco '
                          'no prueban qué archivo cargó PPSSPP.')}
    # Evitar incluso un informe truncado/semiescrito en caso de validación fallida.
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest-usa', type=Path, required=True)
    p.add_argument('--manifest-sonda', type=Path, required=True)
    p.add_argument('--iso-usa', type=Path, required=True)
    p.add_argument('--iso-sonda', type=Path, required=True)
    p.add_argument('--reporte-privado', type=Path, required=True)
    args = p.parse_args()
    result = audit(args.manifest_usa, args.manifest_sonda, args.iso_usa,
                   args.iso_sonda, args.reporte_privado, Path(__file__).resolve().parents[1])
    print(json.dumps({'scene': result['scene'],
                      'candidate_new_magenta_pixels': [p['candidate_new_magenta_pixels'] for p in result['pairs']],
                      'runtime_loaded_iso_identity_proven': False}, ensure_ascii=False))

if __name__ == '__main__':
    main()
