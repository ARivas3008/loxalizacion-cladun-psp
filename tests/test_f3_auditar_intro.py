"""F3 solo PRUEBAS SINTÉTICAS: ni ISO comercial ni PPSSPP en CI."""
from __future__ import annotations
import csv
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import f3_auditar_intro as f3


def cmd(op: int, data: bytes = b'', command_id: int = 3):
    return bytes([op])+struct.pack('<HH',command_id,len(data))+data


def text_cmd(phrase: bytes,op: int = 0x66):
    return cmd(op,struct.pack('<H',len(phrase))+phrase+b'\x00')


def test_record(offset: int, script: str, script_id: int, es: str,
                original: bytes = b'A') -> dict:
    return {
        'grupo_id':f'{offset:06d}', 'origen':f3.SCRIPT_SOURCE,
        'script':script, 'script_id':str(script_id),
        'offset_hex':hex(offset), 'bytes_hex':original.hex().upper(),
        'longitud_original_bytes':str(len(original)),
        'espanol':es, 'original':original.decode('cp932'),
    }


class FakeReader:
    fieldnames=['grupo_id','origen','script','script_id','offset_hex',
                'bytes_hex','longitud_original_bytes','espanol','original']
    def __init__(self,rows): self.rows=rows
    def __iter__(self): return iter(self.rows)


class TestF3Static(unittest.TestCase):
    def test_text_command_exact_span(self):
        one=text_cmd(b'Hello',0x66)
        cmds,text_count,found=f3.parse_commands(one,0,len(one))
        self.assertEqual((cmds,text_count),(1,1))
        self.assertEqual(found,{7:b'Hello'})
    def test_nontext_preserved_in_parser(self):
        data=cmd(0x20,b'\x00\xff')+text_cmd(b'Story',0x69)
        c,t,r=f3.parse_commands(data,0,len(data))
        self.assertEqual((c,t),(2,1))
        self.assertEqual(r,{len(cmd(0x20,b'\x00\xff'))+7:b'Story'})
    def test_empty_text_opcode_is_excluded_from_fields(self):
        data=text_cmd(b'',0x6e)
        self.assertEqual(f3.parse_commands(data,0,len(data))[:2],(1,1))
        self.assertEqual(f3.parse_commands(data,0,len(data))[2],{})
    def test_padding_allowed(self):
        data=text_cmd(b'A')+b'\x00'*12
        self.assertEqual(f3.parse_commands(data,0,len(data))[2],{7:b'A'})
    def test_corrupt_length_denied(self):
        data=bytearray(text_cmd(b'A'));data[3:5]=struct.pack('<H',400)
        with self.assertRaises(ValueError):f3.parse_commands(bytes(data),0,len(data))
    def test_corrupt_internal_nul_denied(self):
        data=bytearray(text_cmd(b'A'));data[-1]=5
        with self.assertRaises(ValueError):f3.parse_commands(bytes(data),0,len(data))
    def test_corrupt_embedded_size_denied(self):
        data=bytearray(text_cmd(b'AB'));data[5:7]=struct.pack('<H',1)
        with self.assertRaises(ValueError):f3.parse_commands(bytes(data),0,len(data))
    def test_unread_nonzero_tail_denied(self):
        data=text_cmd(b'A')+b'\x01'
        with self.assertRaises(ValueError):f3.parse_commands(data,0,len(data))
    def test_invalid_segment_denied(self):
        with self.assertRaises(ValueError):f3.parse_commands(b'\0'*20,8,21)
    def test_all_expected_intro_scripts_named(self):
        self.assertEqual(len(f3.EXPECTED_IDS),7)
        self.assertEqual(set(f3.EXPECTED_IDS.values()),f3.FILES)
    def test_no_priv_report_relative(self):
        with self.assertRaises(ValueError):f3.safe_private_output(Path('report.json'))
    def test_no_priv_report_inside_repo(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises(ValueError):f3.safe_private_output(root/'report.json',root)
    def test_no_priv_report_existing_file(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'file.json';p.write_text('keep')
            with self.assertRaises(ValueError):f3.safe_private_output(p,root/'repo')
            self.assertEqual(p.read_text(),'keep')
    def test_no_priv_report_git_ancestor(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'.git').mkdir()
            with self.assertRaises(ValueError):f3.safe_private_output(root/'report.json',root/'repo')
    def test_no_priv_report_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'link.json';p.symlink_to(root/'missing.json')
            with self.assertRaises(ValueError):f3.safe_private_output(p,root/'repo')


class TestF3DraftSynthetic(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.file=Path(self.tmp.name)/'bor.csv';self.file.write_text('FAKE',encoding='utf-8')
        self.texts={}
        self.rows=[]
        groups=[(100100,'demo1001_00.dsf',44),
                (100101,'demo1001_01.dsf',45),
                (100110,'demo1001_01.dsf',5),
                (100120,'demo1001_01.dsf',3)]
        k=0
        for script_id,script,count in groups:
            for _ in range(count):
                off=10000+k
                es=('BB' if k<85 else 'B' if k<96 else 'A')
                self.rows.append(test_record(off,script,script_id,es))
                self.texts[off]={'raw':b'A','script_id':script_id,'script_file':script}
                k+=1
        self.rows.extend([{'script':''} for _ in range(9237-len(self.rows))])
        self.assertEqual((k,len(self.rows)),(97,9237))
    def run_audit(self):
        with patch.object(f3.csv,'DictReader',return_value=FakeReader(self.rows)):
            return f3.audit_draft(self.file,self.texts)
    def test_evaluates_synthetic_85_11_1(self):
        v=self.run_audit()
        self.assertEqual(v['classification'],{
            'BLOQUEADO_DIFERENTE_LONGITUD':85,
            'CANDIDATO_LONGITUD_COMPATIBLE':11,
            'SIN_CAMBIO':1,
        })
        self.assertFalse(v['different_length_script_changes_authorized'])
        self.assertEqual(v['original_corpus_rows'],9237)
    def test_missing_corpus_row_denied(self):
        self.rows.pop()
        with self.assertRaises(ValueError):self.run_audit()
    def test_missing_intro_row_denied(self):
        self.rows[0]['script']='other'
        with self.assertRaises(ValueError):self.run_audit()
    def test_duplicate_offset_denied(self):
        self.rows[1]['offset_hex']=self.rows[0]['offset_hex']
        with self.assertRaises(ValueError):self.run_audit()
    def test_missing_iso_offset_denied(self):
        self.rows[0]['offset_hex']='0xffff'
        with self.assertRaises(ValueError):self.run_audit()
    def test_wrong_source_hex_denied(self):
        self.rows[0]['bytes_hex']='42'
        with self.assertRaises(ValueError):self.run_audit()
    def test_wrong_script_id_denied(self):
        self.rows[0]['script_id']='100101'
        with self.assertRaises(ValueError):self.run_audit()
    def test_wrong_original_text_denied(self):
        self.rows[0]['original']='wrong'
        with self.assertRaises(ValueError):self.run_audit()
    def test_wrong_source_field_denied(self):
        self.rows[0]['origen']='WRONG'
        with self.assertRaises(ValueError):self.run_audit()
    def test_wrong_length_field_denied(self):
        self.rows[0]['longitud_original_bytes']='44'
        with self.assertRaises(ValueError):self.run_audit()
    def test_unencodable_spanish_denied(self):
        self.rows[0]['espanol']='🙂'
        with self.assertRaises(UnicodeError):self.run_audit()
    def test_untranslated_candidate_cannot_be_silently_accepted(self):
        self.rows[0]['espanol']=''
        with self.assertRaises(ValueError):self.run_audit()
    def test_distinct_intro_scripts_reported(self):
        r=self.run_audit()
        self.assertEqual(set(r['by_script_id']),{'100100','100101','100110','100120'})


if __name__=='__main__':
    unittest.main()
