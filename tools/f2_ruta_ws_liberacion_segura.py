#!/usr/bin/env python3
"""F2: reproducir pasos PPSSPP por WS, con checkpoints manuales y RELEASE verificado.

No obtiene imágenes ni certifica TUIKA. Una respuesta demorada de press no se
interpreta como un botón liberado; siempre se envía un release explícito.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = 'cladun.f2.ws_input_route.v1'
BUTTONS = ('cross', 'circle', 'triangle', 'square', 'up', 'down', 'left', 'right',
           'start', 'select', 'ltrigger', 'rtrigger')
RELEASE_ALL = {button: False for button in BUTTONS}


def validate_steps(data):
    if not isinstance(data, dict) or set(data) != {'schema', 'steps'} or data['schema'] != SCHEMA:
        raise ValueError('Esquema de ruta incorrecto')
    steps = data['steps']
    if not isinstance(steps, list) or not 1 <= len(steps) <= 120:
        raise ValueError('Número de pasos fuera de límite')
    result = []
    have_checkpoint = False
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            raise ValueError(f'Paso {i} no es objeto')
        if step.get('kind') == 'checkpoint':
            if set(step) != {'kind', 'label'} or not isinstance(step['label'], str):
                raise ValueError('Checkpoint debe tener una etiqueta')
            label = step['label']
            if not re.fullmatch(r'[\wÁÉÍÓÚáéíóúñÑüÜ¿¡«»ō.,:() /-]{3,100}', label):
                raise ValueError('Etiqueta incorrecta o potencialmente peligrosa')
            have_checkpoint = True
        elif step.get('kind') == 'press':
            if set(step) != {'kind', 'button', 'frames'}:
                raise ValueError('Un press solo admite button y frames')
            if step['button'] not in BUTTONS or type(step['frames']) is not int or not 1 <= step['frames'] <= 120:
                raise ValueError('Botón o duración inválidos')
            if not have_checkpoint:
                raise ValueError('Prohibido enviar botones antes del checkpoint visual')
        else:
            raise ValueError(f'Acción no permitida en el paso {i}')
        result.append(step.copy())
    if not have_checkpoint:
        raise ValueError('Falta checkpoint')
    return result


def _release(client, *, emergency=False):
    """Release explícito: si falla la confirmación, no afirmar liberación."""
    # En caso de timeout de 'press' el socket quizá siga abierto; enviar antes
    # de esperar para minimizar una pulsación que siga activa.
    if emergency:
        client.conn.send(json.dumps({'event': 'input.buttons.send', 'buttons': RELEASE_ALL}))
    client.request('input.buttons.send', buttons=RELEASE_ALL)


def execute(client, steps, confirm):
    """Sólo confirmar 'completado' tras liberar todas las teclas con respuesta WS."""
    steps = validate_steps({'schema': SCHEMA, 'steps': steps})
    history = []
    error = None
    released = False
    try:
        _release(client)
        for item in steps:
            if item['kind'] == 'checkpoint':
                if not confirm(item['label']):
                    raise RuntimeError('Checkpoint visual no confirmado: ' + item['label'])
                history.append({'kind': 'checkpoint', 'label': item['label'], 'confirmed_by_operator': True})
                continue
            status = client.request('cpu.status')
            if status.get('stepping') is not False:
                raise RuntimeError('CPU no ejecutándose: press no avanzaría frames')
            acknowledged = False
            try:
                client.request('input.buttons.press', button=item['button'], duration=item['frames'])
                acknowledged = True
                history.append({'kind': 'press', 'button': item['button'], 'frames': item['frames'], 'reply_received': True})
            finally:
                # Incluso si press expiró o el socket cerró.
                _release(client, emergency=not acknowledged)
    except Exception as exc:
        error = repr(exc)
    finally:
        try:
            _release(client)
            released = True
        except Exception as exc:
            error = (error + '; ' if error else '') + 'release_unconfirmed=' + repr(exc)
    result = {'commands_accepted': len(history), 'steps_declared': len(steps),
              'history': history, 'explicit_release_acknowledged': released,
              'completed': error is None and released and len(history) == len(steps),
              'error': error, 'gameplay_scene_proven': False, 'tuika_runtime_proven': False,
              'capture_synchronized': False}
    return result


def _private_output(path):
    output = Path(path)
    root = Path(__file__).resolve().parents[1]
    resolved = output.resolve(strict=False)
    if (not output.is_absolute() or output.suffix.lower() != '.json'
            or resolved == root or root in resolved.parents or resolved.exists()
            or any((q / '.git').exists() for q in resolved.parents)):
        raise ValueError('Informe privado nuevo fuera de cualquier repo Git')
    return resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ruta-json', type=Path, required=True)
    parser.add_argument('--iso-privada', type=Path, required=True)
    parser.add_argument('--tipo', choices=['usa', 'sonda', 'f1'], required=True)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--port', type=int, default=24192)
    parser.add_argument('--informe-privado', type=Path, required=True)
    opts = parser.parse_args()
    if not sys.stdin.isatty():
        parser.error('Sin terminal interactiva no se pueden comprobar escenas reales')
    route_bytes = opts.ruta_json.read_bytes()
    steps = validate_steps(json.loads(route_bytes))
    output = _private_output(opts.informe_privado)
    try:
        from tools.f2_ws_procedencia_ppsspp import correlate
        from tools.f2_ppsspp_ws_1204 import Client
    except ModuleNotFoundError:
        from f2_ws_procedencia_ppsspp import correlate
        from f2_ppsspp_ws_1204 import Client
    import websocket
    witness = correlate(opts.pid, opts.port, opts.iso_privada, opts.tipo)
    if not (witness['websocket_listener_owned_by_same_ppsspp_pid']
            and witness['iso_fd_same_inode_open_before_after']
            and witness['argv_exact_iso_match'] and witness['ws']['cpu_running']):
        raise RuntimeError('ISO/WS/PID/CPU no autenticados')
    conn = websocket.create_connection(f'ws://127.0.0.1:{opts.port}/debugger',
                                       subprotocols=['debugger.ppsspp.org'], timeout=35,
                                       http_proxy_host=None)
    try:
        if conn.getsubprotocol() != 'debugger.ppsspp.org':
            raise RuntimeError('Subprotocolo WS incorrecto')
        client = Client(conn)
        version = client.request('version', name='cladun-f2-safe-route', version='1')
        if version.get('name') != 'PPSSPP' or version.get('version') != 'v1.20.4':
            raise RuntimeError('PPSSPP no es 1.20.4')
        if client.request('game.status').get('game', {}).get('id') != 'NPUH10072':
            raise RuntimeError('Juego incorrecto')
        def confirm(label):
            print(f'VERIFICAR EN X11 (no es lectura automática): {label}')
            return input('Escriba exactamente CONFIRMAR: ').strip() == 'CONFIRMAR'
        outcome = execute(client, steps, confirm)
    finally:
        conn.close()
    outcome.update({'schema': SCHEMA + '.result',
                    'input_route_sha256': hashlib.sha256(route_bytes).hexdigest(),
                    'role': opts.tipo, 'iso_sha256': witness['iso_sha256'],
                    'ws_iso_pid_socket_witness': True,
                    'x11_screenshot_generated': False, 'ge_dump_generated': False})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as f:
        json.dump(outcome, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'completed': outcome['completed'],
                      'release_acknowledged': outcome['explicit_release_acknowledged'],
                      'report': str(output)}, ensure_ascii=False))
    if not outcome['completed']:
        raise SystemExit('Ruta abortada; NO asumir botones liberados si no hay ACK')


if __name__ == '__main__':
    main()
