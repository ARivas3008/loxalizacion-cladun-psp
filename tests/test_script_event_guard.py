"""Prevencion de corrupcion de eventos; sin assets comerciales en tests."""
from __future__ import annotations
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from script_event_guard import audit_script_rebuild
from integrar_parche_seguro import text_command_rebuild


def fixture():
    table = bytearray(16 + 32 * 1625)
    struct.pack_into('<I', table, 0, 1625)
    original = bytearray()
    for i in range(1625):
        struct.pack_into('<I', table, 16 + i * 32 + 4, len(original))
        if i == 0:
            original += b'\x66\x01\x00\x08\x00\x05\x00Hello\0'
            original += b'\x01\x02\x00\x04\x00\xaa\xbb\xcc\xdd'
        original += b'\0' * (-len(original) % 16 or 16)
    return bytes(original), bytes(table)

class EventGuardTest(unittest.TestCase):
    def test_noop_keeps_every_opcode_and_offset(self):
        a,t=fixture()
        info=audit_script_rebuild(a,t,a,t,{ },require_fixed_offsets=True)
        self.assertTrue(info['all_command_offsets_preserved'])
        self.assertEqual(info['nontext_commands_byte_exact'],1)

    def test_same_length_span_is_strongly_event_preserving(self):
        a,t=fixture()
        translations={7:(b'Hello',b'Adios','000001')}
        b,u=text_command_rebuild(a,t,translations)
        info=audit_script_rebuild(a,t,b,u,translations,require_fixed_offsets=True)
        self.assertEqual(info['text_commands_replaced'],1)
        self.assertEqual(info['moved_command_offsets'],0)

    def test_resized_text_is_not_claimed_event_safe(self):
        a,t=fixture()
        translations={7:(b'Hello',b'Buenos dias','000001')}
        b,u=text_command_rebuild(a,t,translations)
        info=audit_script_rebuild(a,t,b,u,translations)
        self.assertGreater(info['moved_nontext_command_offsets'],0)
        self.assertFalse(info['all_command_offsets_preserved'])
        with self.assertRaisesRegex(ValueError,'Bloqueo de seguridad'):
            audit_script_rebuild(a,t,b,u,translations,require_fixed_offsets=True)

    def test_unknown_event_payload_mutation_rejected(self):
        a,t=fixture()
        b=bytearray(a); b[19]^=1
        with self.assertRaisesRegex(ValueError,'payload no textual'):
            audit_script_rebuild(a,t,bytes(b),t,{})

    def test_table_ids_mutation_rejected(self):
        a,t=fixture()
        u=bytearray(t);u[16]=1
        with self.assertRaisesRegex(ValueError,'metadatos'):
            audit_script_rebuild(a,t,a,bytes(u),{})

    def test_unexpected_text_edit_rejected(self):
        a,t=fixture()
        b=bytearray(a);b[7:12]=b'Wrong'
        with self.assertRaisesRegex(ValueError,'Texto no autorizado'):
            audit_script_rebuild(a,t,bytes(b),t,{})

if __name__=='__main__':unittest.main()
