#!/usr/bin/env python3
"""Compara evidencia privada X11 A/B sin elevarla a framebuffer PSP ni causalidad TUIKA.

Acepta exclusivamente manifiestos v1 del capturador f2_x11_ppsspp_procfs_capture.
No produce ni modifica imágenes: solo métricas numéricas en JSON privado.
Es una comparación de bytes/PNG y declaraciones, NO certificación de gameplay.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image

try:
    from tools.f2_cotejar_capturas_tuika import (compare_pair, file_sha, private_path,
                                                  USA_SHA, PROBE_SHA, ISO_SIZE, MAX_IMAGE_BYTES)
except ModuleNotFoundError:
    from f2_cotejar_capturas_tuika import (compare_pair, file_sha, private_path,
                                           USA_SHA, PROBE_SHA, ISO_SIZE, MAX_IMAGE_BYTES)

SCHEMA = 'cladun.f2.x11_pid_procfs_evidence.v1'
SIZE = (960, 544)
HEX = re.compile(r'^[0-9a-f]{64}$')
LABEL = re.compile(r'^[A-Za-z0-9_-]{1,64}$')


def load_x11(manifest_path: Path, repo: Path, role: str, expected_sha: str) -> dict:
    """Comprueba el contrato de manifest y el PNG real, no la honestidad del emulador."""
    path = private_path(manifest_path, repo)
    with path.open(encoding='utf-8') as stream:
        report = json.load(stream)
    if (report.get('schema') != SCHEMA or
        report.get('runtime') != 'REAL_X11_PPSSPP_1.20.4' or
        report.get('source_iso_role') != role or
        report.get('source_iso_sha256') != expected_sha or
        report.get('this_is_psp_framebuffer') is not False or
        report.get('runtime_loaded_iso_identity_proven') is not False or
        report.get('mips_ram_ge_vram_proven') is not False):
        raise ValueError('Manifiesto X11 ambiguo, incompatible o proclama evidencia no acreditada')
    win, shot, paired = report.get('x11'), report.get('screenshot_x11'), report.get('paired')
    if not isinstance(win, dict) or not isinstance(shot, dict) or not isinstance(paired, dict):
        raise ValueError('Faltan ventana, PNG o testigo de /proc')
    pid = win.get('window_pid')
    if (not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0 or
        win.get('window_size_960x544') is not True or
        win.get('window_title_is_cladun') is not True or
        (win.get('width'), win.get('height')) != SIZE or
        report.get('x11_window_pid_correlated_to_procfs') is not True or
        paired.get('pid_starttime_stable') is not True or
        paired.get('same_inode_open_before_and_after') is not True):
        raise ValueError('Testigo X11/PID/ISO incompleto o incongruente')
    name = shot.get('filename')
    if (not isinstance(name, str) or not name or Path(name).name != name or
        name in ('.', '..') or not name.lower().endswith('.png')):
        raise ValueError('Nombre del PNG peligroso')
    pic_path = private_path(path.parent / name, repo)
    if pic_path.is_symlink() or pic_path.suffix.lower() != '.png':
        raise ValueError('PNG enlazado o extensión inválida')
    n = pic_path.stat().st_size
    if (n < 24 or n > MAX_IMAGE_BYTES or shot.get('bytes') != n or
        shot.get('width') != SIZE[0] or shot.get('height') != SIZE[1] or
        not isinstance(shot.get('sha256'), str) or not HEX.fullmatch(shot['sha256']) or
        file_sha(pic_path) != shot['sha256']):
        raise ValueError('PNG X11 no coincide con bytes/dimensiones/SHA declarados')
    with Image.open(pic_path) as im:
        if im.format != 'PNG' or im.size != SIZE:
            raise ValueError('La imagen no es el PNG X11 960x544 requerido')
        im.load()
        image = im.convert('RGB')
    return {'manifest_sha256': file_sha(path), 'png_sha256': shot['sha256'],
            'image': image, 'window_pid_declared': pid,
            'corroborated_iso_fd_open_declared': True}


def _roi(value: tuple[int, int, int, int] | None) -> tuple[int, int, int, int] | None:
    if value is None:
        return None
    if len(value) != 4 or any(type(x) is not int for x in value):
        raise ValueError('ROI necesita cuatro enteros x,y,ancho,alto')
    x,y,w,h = value
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > SIZE[0] or y + h > SIZE[1]:
        raise ValueError('ROI fuera de la captura X11 de 960x544')
    return (x,y,x+w,y+h)


def audit(usa_manifest: Path, probe_manifest: Path, usa_iso: Path, probe_iso: Path,
          output: Path, repo: Path, scene: str, roi: tuple[int, int, int, int] | None = None) -> dict:
    """No atestigua escena ni sincronización; el operador debe aportar la observación."""
    if not isinstance(scene, str) or not LABEL.fullmatch(scene):
        raise ValueError('Identificador de escena inválido')
    box = _roi(roi)
    output = private_path(output, repo, for_output=True)
    usa_iso, probe_iso = private_path(usa_iso, repo), private_path(probe_iso, repo)
    if usa_iso == probe_iso:
        raise ValueError('USA y sonda deben estar en archivos diferentes')
    for iso, sha in ((usa_iso, USA_SHA), (probe_iso, PROBE_SHA)):
        if iso.stat().st_size != ISO_SIZE or file_sha(iso) != sha:
            raise ValueError('ISO auténtica ausente o SHA/tamaño alterados')
    ma = private_path(usa_manifest, repo)
    mb = private_path(probe_manifest, repo)
    if ma.parent == mb.parent or ma == mb:
        raise ValueError('Se exigen dos sesiones privadas independientes')
    a = load_x11(ma, repo, 'usa', USA_SHA)
    b = load_x11(mb, repo, 'sonda', PROBE_SHA)
    whole = compare_pair(a['image'], b['image'])
    if box is None:
        cropped = None
    else:
        cropped = compare_pair(a['image'].crop(box), b['image'].crop(box))
    result = {
        'schema': 'cladun.f2.tuika_x11_ab_file_comparison.v1',
        'source': 'DOS_MANIFIESTOS_X11_PRIVADOS_NO_FRAMEBUFFER_PSP',
        'operator_scene_label_unverified': scene,
        'source_iso_sha256_verified_from_disk': {'usa':USA_SHA, 'sonda':PROBE_SHA},
        'manifest_sha256': {'usa':a['manifest_sha256'], 'sonda':b['manifest_sha256']},
        'png_sha256': {'usa':a['png_sha256'], 'sonda':b['png_sha256']},
        'declared_x11_window_pid': {'usa':a['window_pid_declared'], 'sonda':b['window_pid_declared']},
        'declared_procfs_fd_correlations_not_independently_replayed': True,
        'full_x11_frame': whole,
        'roi_xyxy_exclusive': list(box) if box is not None else None,
        'roi_metrics': cropped,
        'identical_png_sha256': a['png_sha256'] == b['png_sha256'],
        'visual_scene_alignment_proven': False,
        'gameplay_event_proven': False,
        'psp_framebuffer_used': False,
        'emulated_frame_timing_verified': False,
        'loaded_iso_identity_proven': False,
        'tuika_texture_gpu_identity_proven': False,
        'mips_ram_ge_vram_pipeline_proven': False,
        'warning': ('X11 verifica colores, no sincroniza eventos ni determina la textura causal. '
                    'Magenta nativo en SYSTEM PRiSM no es evidencia positiva; '
                    '0 diferencias tampoco prueba ausencia de TUIKA. Revisar escena y GE aparte.'),
        'commercial_pngs_or_iso_embedded_in_report': False,
    }
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
    p.add_argument('--escena', required=True, help='Etiqueta declarada; NO confirma sincronización')
    p.add_argument('--roi', nargs=4, type=int, metavar=('X','Y','ANCHO','ALTO'))
    args = p.parse_args()
    result = audit(args.manifest_usa, args.manifest_sonda,
                   args.iso_usa, args.iso_sonda, args.reporte_privado,
                   Path(__file__).resolve().parents[1], args.escena,
                   tuple(args.roi) if args.roi else None)
    print(json.dumps({'full_frame_different_pixels':result['full_x11_frame']['different_pixels'],
                      'candidate_new_magenta':result['full_x11_frame']['candidate_new_magenta_pixels'],
                      'visual_scene_alignment_proven':False,
                      'tuika_texture_gpu_identity_proven':False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
