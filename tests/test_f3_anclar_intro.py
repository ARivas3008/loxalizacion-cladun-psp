"""F3-R5: tests sintéticos y comprobación del borrador real con anclaje ISO.

No requiere ISO comercial en CI. Un PASS no demuestra interpretación MIPS.
"""
from __future__ import annotations
import copy
from pathlib import Path
import unittest
from tools import f3_anclar_intro as f3

ROOT=Path(__file__).resolve().parents[1]


def fixture():
    blocks=[{'block_index':0,'script_id':100100,'name':'demo1001_00.dsf',
             'command_count':7,'source_start':0,'source_end':100}]
    spans=[];data=[(7,0,b'A','BB'),(25,2,b'AB','A'),(50,5,b'XYZ','XYZ')]
    rows=[]
    for off,order,raw,es in data:
        spans.append({'offset':off,'script_id':100100,'script_file':'demo1001_00.dsf',
                      'block_index':0,'command_order':order,'source_length':len(raw),
                      'following_commands':6-order})
        rows.append({'grupo_id':str(off),'origen':'SCRIPT.SDT/SCRIPT.DAT','script':'demo1001_00.dsf',
                     'script_id':'100100','offset_hex':hex(off),'bytes_hex':raw.hex(),
                     'longitud_original_bytes':str(len(raw)),'original':raw.decode('cp932'),'espanol':es})
    anchor=f3.anchor_hash([(s,item[2]) for s,item in zip(spans,data)])
    return {'schema':'cladun.f3.intro_source_geometry.v2','blocks':blocks,
            'text_spans':spans,'source_and_order_sha256':anchor},rows


class TestSyntheticSourceAnchor(unittest.TestCase):
    def setUp(self):self.geo,self.rows=fixture()

    def test_root_stable_for_shuffled_records(self):
        pairs=[(x,bytes.fromhex(y['bytes_hex'])) for x,y in zip(self.geo['text_spans'],self.rows)]
        self.assertEqual(f3.anchor_hash(pairs),f3.anchor_hash(list(reversed(pairs))))

    def test_source_and_order_root_rejects_mutated_byte(self):
        wrong=copy.deepcopy(self.rows)
        wrong[0]['bytes_hex']='42';wrong[0]['original']='B'
        with self.assertRaisesRegex(ValueError,'Raíz SHA'):
            f3.evaluate_rows(wrong,self.geo,canonical=False)

    def test_duplicate_offset_is_rejected(self):
        wrong=copy.deepcopy(self.rows);wrong[1]['offset_hex']=wrong[0]['offset_hex']
        with self.assertRaises(ValueError):f3.evaluate_rows(wrong,self.geo,canonical=False)

    def test_invalid_script_id_is_rejected(self):
        wrong=copy.deepcopy(self.rows);wrong[1]['script_id']='222222'
        with self.assertRaises(ValueError):f3.evaluate_rows(wrong,self.geo,canonical=False)

    def test_invalid_original_text_is_rejected(self):
        wrong=copy.deepcopy(self.rows);wrong[1]['original']='bad'
        with self.assertRaises(ValueError):f3.evaluate_rows(wrong,self.geo,canonical=False)

    def test_missing_span_is_rejected(self):
        with self.assertRaises(ValueError):f3.evaluate_rows(self.rows[:-1],self.geo,canonical=False)

    def test_wrong_source_is_rejected(self):
        wrong=copy.deepcopy(self.rows);wrong[1]['origen']='OTHER'
        with self.assertRaises(ValueError):f3.evaluate_rows(wrong,self.geo,canonical=False)

    def test_unencodable_spanish_is_rejected(self):
        wrong=copy.deepcopy(self.rows);wrong[1]['espanol']='🙂'
        with self.assertRaises(UnicodeEncodeError):f3.evaluate_rows(wrong,self.geo,canonical=False)

    def test_shift_can_cancel_and_no_relocation_is_approved(self):
        result=f3.evaluate_rows(self.rows,self.geo,canonical=False)
        self.assertEqual(result['change_counts'],{'unequal':2,'unchanged':1})
        p=result['simple_concat_projection'][0]
        self.assertEqual(p['net_text_byte_delta'],0)
        self.assertEqual(p['hypothetical_commands_with_changed_start'],2)
        self.assertEqual(p['hypothetical_max_absolute_start_shift'],1)
        self.assertFalse(result['relocation_authorized'])
        self.assertTrue(result['preserve_event_safe_only'])

    def test_unbalanced_positive_shift(self):
        wrong=copy.deepcopy(self.rows);wrong[1]['espanol']='CD'
        p=f3.evaluate_rows(wrong,self.geo,canonical=False)['simple_concat_projection'][0]
        self.assertEqual(p['net_text_byte_delta'],1)
        self.assertEqual(p['hypothetical_commands_with_changed_start'],6)

    def test_geometry_inconsistent_following_count_rejected(self):
        wrong=copy.deepcopy(self.geo);wrong['text_spans'][0]['following_commands']+=1
        with self.assertRaises(ValueError):f3.check_geometry(wrong,require_canonical=False)

    def test_geometry_duplicate_order_rejected(self):
        wrong=copy.deepcopy(self.geo);wrong['text_spans'][1]['command_order']=0
        with self.assertRaises(ValueError):f3.check_geometry(wrong,require_canonical=False)

    def test_git_blob_hash_uses_git_header(self):
        import hashlib
        self.assertEqual(f3.git_blob_hash(b'abc'),hashlib.sha1(b'blob 3\0abc').hexdigest())

    def test_spanish_private_a1_b3_roundtrip(self):
        sample='¿Qué día es? ¡Sí, señor! Ñandú, ü, ō.'
        self.assertEqual(f3.decode_spanish(f3.encode_spanish(sample)),sample)


class TestRealRepoDraftAgainstAuthenticIsoAnchor(unittest.TestCase):
    def test_real_canonical_draft_matches_97_iso_original_spans(self):
        geometry=ROOT/f3.GEOMETRY_REL
        draft=ROOT/f3.DRAFT_REL
        self.assertTrue(geometry.is_file(),f'Falta manifiesto de ISO: {geometry}')
        self.assertTrue(draft.is_file(),f'Falta borrador real: {draft}')
        r=f3.audit(draft,geometry)
        self.assertEqual(r['source_root_sha256'],f3.ANCHOR_SHA256)
        self.assertEqual(r['change_counts'],{'unequal':85,'same_length_changed':11,'unchanged':1})
        self.assertEqual((r['source_bytes'],r['spanish_bytes']),(2728,2859))
        self.assertFalse(r['relocation_authorized'])
        self.assertFalse(r['runtime_ppsspp_executed'])


if __name__=='__main__':unittest.main()
