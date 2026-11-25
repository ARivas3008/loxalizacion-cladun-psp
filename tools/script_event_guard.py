#!/usr/bin/env python3
"""Auditoria independiente de eventos para SCRIPT.DAT / SCRIPT.TBL.

NO interpreta opcodes desconocidos ni presume que reconstruir indices de bloque
repara referencias ocultas a offsets de comandos. Compara cada comando por
orden, exige payload no textual byte-a-byte identico y separa estos hechos de
la estabilidad de offsets (una garantia mas fuerte, pero aun no PPSSPP).
"""
from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import Mapping

TEXT_OPS = frozenset((0x66, 0x69, 0x6E))
EXPECTED_BLOCKS = 1625


def require(ok, message):
    if not ok:
        raise ValueError(message)


def u16(blob, pos):
    return struct.unpack_from('<H', blob, pos)[0]


def u32(blob, pos):
    return struct.unpack_from('<I', blob, pos)[0]


@dataclass(frozen=True)
class Command:
    block: int
    order: int
    offset: int
    code: int
    instruction_id: int
    raw: bytes
    content: bytes | None


def read_commands(data: bytes, table: bytes) -> tuple[list[Command], list[int]]:
    require(len(table) >= 16 and u32(table, 0) == EXPECTED_BLOCKS and
            len(table) == 16 + 32 * EXPECTED_BLOCKS,
            'Tabla de scripts inesperada: no se permite reconstruccion')
    starts = [u32(table, 16 + 32 * i + 4) for i in range(EXPECTED_BLOCKS)] + [len(data)]
    require(starts[0] == 0 and starts == sorted(starts) and
            all(p % 16 == 0 for p in starts[:-1]) and starts[-1] <= len(data),
            'Offsets de SCRIPT.TBL invalidos')
    commands = []
    for block in range(EXPECTED_BLOCKS):
        start, limit = starts[block:block + 2]
        pos, order = start, 0
        while pos + 5 <= limit:
            if not any(data[pos:limit]):
                break
            cmd_len = u16(data, pos + 3)
            end = pos + 5 + cmd_len
            require(end <= limit, f'Comando fuera de bloque {block}, offset {pos:#x}')
            raw = data[pos:end]
            code, cid = raw[0], u16(raw, 1)
            content = None
            if code in TEXT_OPS:
                require(cmd_len >= 3 and u16(raw, 5) + 3 == cmd_len and raw[-1] == 0,
                        f'Opcode textual corrupto en {pos:#x}')
                content = raw[7:-1]
            commands.append(Command(block, order, pos, code, cid, raw, content))
            pos, order = end, order + 1
        require(not any(data[pos:limit]), f'Padding no nulo en bloque {block}')
    return commands, starts


def audit_script_rebuild(original_data: bytes, original_table: bytes,
                         new_data: bytes, new_table: bytes,
                         expected: Mapping[int, tuple[bytes, bytes, str]],
                         *, require_fixed_offsets: bool = False) -> dict:
    """Bloquea cambios en opcodes, IDs, argumentos de eventos y textos inesperados.

    Invariante fuerte opcional: TODO comando retiene el mismo offset y
    SCRIPT.TBL queda byte-identico. Si falla, no declarar preservacion de
    control de flujo aun si los bytes no textuales coinciden.
    """
    before, old_starts = read_commands(original_data, original_table)
    after, new_starts = read_commands(new_data, new_table)
    require(len(before) == len(after), 'Se insertaron/eliminaron comandos de evento')
    require(original_table[:16] == new_table[:16], 'Cabecera de SCRIPT.TBL cambiada')
    restored = bytearray(new_table)
    for i in range(EXPECTED_BLOCKS):
        struct.pack_into('<I', restored, 16 + 32 * i + 4, old_starts[i])
    require(bytes(restored) == original_table,
            'SCRIPT.TBL cambio IDs, nombres u otros metadatos ajenos a offsets')

    applied = set()
    moved_commands = 0
    moved_nontext = 0
    moving_blocks = set()
    unchanged_nontext = 0
    altered_text = 0
    for a, b in zip(before, after):
        require((a.block, a.order, a.code, a.instruction_id) ==
                (b.block, b.order, b.code, b.instruction_id),
                f'Se cambio orden, opcode o ID del evento en bloque {a.block}, instruccion {a.order}')
        if a.offset != b.offset:
            moved_commands += 1
            moving_blocks.add(a.block)
            if a.code not in TEXT_OPS:
                moved_nontext += 1
        if a.content is None:
            require(a.raw == b.raw,
                    f'El payload no textual del evento cambio: bloque {a.block}, instruccion {a.order}')
            unchanged_nontext += 1
        elif a.content != b.content:
            slot = a.offset + 7
            require(slot in expected,
                    f'Texto no autorizado en {slot:#x}, bloque {a.block}')
            old, new, gid = expected[slot]
            require(a.content == old and b.content == new,
                    f'Bytes de texto no coinciden con el corpus: {gid}')
            applied.add(slot)
            altered_text += 1
        else:
            require(a.raw == b.raw,
                    f'Header de comando textual cambiado sin traduccion: {a.block}/{a.order}')
    require(applied == set(expected),
            f'Traduciones no insertadas: {len(set(expected) - applied)}')
    moved_starts = sum(a != b for a, b in zip(old_starts[:-1], new_starts[:-1]))
    offset_stable = moved_commands == moved_starts == 0
    if require_fixed_offsets:
        require(offset_stable and len(new_data) == len(original_data),
                f'Bloqueo de seguridad: {moved_commands} comandos y {moved_starts} scripts '
                'cambiaron sus offsets; el motor podria referenciarlos')
    return {
        'total_script_blocks': EXPECTED_BLOCKS,
        'total_commands': len(before),
        'nontext_commands_byte_exact': unchanged_nontext,
        'text_commands_replaced': altered_text,
        'opcode_instruction_id_order_changes': 0,
        'nontext_payload_changes': 0,
        'table_metadata_changes_outside_start_offsets': 0,
        'moved_command_offsets': moved_commands,
        'moved_nontext_command_offsets': moved_nontext,
        'moved_script_starts': moved_starts,
        'script_blocks_with_moved_commands': len(moving_blocks),
        'all_command_offsets_preserved': offset_stable,
        'event_logic_runtime_certified': False,
        'control_flow_reference_model_verified': False,
    }
