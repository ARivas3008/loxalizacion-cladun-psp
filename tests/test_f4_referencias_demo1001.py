"""Pruebas puramente sintéticas; no representan ejecución PSP."""
import struct
import unittest
from dataclasses import dataclass
from tools.f4_referencias_demo1001 import scan_numeric_matches

@dataclass
class Cmd:
    block:int
    offset:int
    code:int
    raw:bytes
    content:bytes|None=None

def cmd(b,o,code,payload=b'',text=None):
    return Cmd(b,o,code,bytes([code])+b'\x01\x00'+struct.pack('<H',len(payload))+payload,text)

class NumericF4Tests(unittest.TestCase):
    def setUp(self):
        self.starts=[0,64,128]
        self.ids=[100100,999999]
        self.names=['demo1001_00.dsf','other.dsf']
    def scan(self,commands):return scan_numeric_matches(commands,self.starts,self.ids,self.names)
    def test_external_script_id_is_just_a_candidate(self):
        d=self.scan([cmd(1,64,0x0A,struct.pack('<I',100100))])
        self.assertEqual(d['candidate_counts']['u32_igual_ID_script_demo1001'],1)
        self.assertFalse(d['semantic_MIPS_verified'])
    def test_intro_relative_command_hit(self):
        d=self.scan([cmd(0,0,2,struct.pack('<I',32)),cmd(0,32,1,b'')])
        self.assertEqual(d['candidate_counts']['u32_igual_offset_relativo_comando_mismo_bloque'],1)
    def test_text_payload_ignored(self):
        d=self.scan([cmd(0,0,0x66,struct.pack('<I',100100),text=b'fake')])
        self.assertEqual(d['candidate_counts'],{})
    def test_zero_is_not_pointer(self):
        d=self.scan([cmd(0,0,2,b'\x00'*4)])
        self.assertEqual(d['candidate_counts'],{})
    def test_misaligned_candidates_report_alignment(self):
        d=self.scan([cmd(1,64,10,b'\xff'+struct.pack('<I',100100))])
        self.assertEqual(d['candidate_payload_alignment_mod4'][0]['payload_offset_mod4'],1)
    def test_invalid_table_lengths(self):
        with self.assertRaises(ValueError):scan_numeric_matches([],[],[],[])
    def test_reject_duplicate_command_starts(self):
        with self.assertRaises(ValueError):self.scan([cmd(0,0,1),cmd(0,0,2)])
    def test_outside_intro_relative_does_not_count(self):
        d=self.scan([cmd(1,64,2,struct.pack('<I',32)),cmd(1,96,1,b'')])
        self.assertEqual(d['candidate_counts'],{})
    def test_never_authorizes_relocation(self):
        d=self.scan([cmd(1,64,10,struct.pack('<I',100100))])
        self.assertFalse(d['relocation_authorized'])
    def test_intro_block_starts_candidate(self):
        self.starts=[16,64,128]
        d=self.scan([cmd(1,64,2,struct.pack('<I',16))])
        self.assertEqual(d['candidate_counts']['u32_igual_inicio_bloque_demo1001'],1)

if __name__=='__main__':unittest.main()
