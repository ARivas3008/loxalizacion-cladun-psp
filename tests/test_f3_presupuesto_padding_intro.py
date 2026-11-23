"""F3-R6: tests sintéticos y cotejo CI contra CSV real sin ISO comercial."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import unittest
from tools import f3_presupuesto_padding_intro as f3

ROOT=Path(__file__).resolve().parents[1]
DELTAS={100000:(0,0),100100:(-1,268),100190:(0,0),100101:(115,298),
        100191:(0,0),100110:(15,10),100120:(2,12)}

def fixtures():
    geo=f3.anchor.load_geometry(ROOT/f3.anchor.GEOMETRY_REL)
    padding=json.loads((ROOT/f3.PADDING_REL).read_text(encoding='utf-8'))
    projected=[{'script_id':b['script_id'],'source_commands':b['command_count'],
       'net_text_byte_delta':DELTAS[b['script_id']][0],
       'hypothetical_commands_with_changed_start':DELTAS[b['script_id']][1]}
       for b in geo['blocks']]
    return geo,padding,projected

class TestPaddingSynthetic(unittest.TestCase):
    def setUp(self):self.geo,self.pad,self.projected=fixtures()

    def test_7_original_padding_rows_canonical(self):
        self.assertEqual(len(f3.validate_padding(self.pad,self.geo)),7)
        self.assertEqual(sum(row[5] for row in self.pad['padding_rows']),48)

    def test_min_144_extra_bytes_three_blocks(self):
        r=f3.project_capacity(self.pad,self.geo,self.projected)
        self.assertEqual(r['totals']['blocks_that_cannot_fit_existing_allocation'],3)
        self.assertEqual(r['totals']['min_additional_capacity_if_each_block_individually_16_aligned'],144)
        self.assertEqual(r['totals']['hypothetical_internal_command_start_changes'],588)
        self.assertFalse(r['relocation_authorized'])

    def test_script_100100_shrinks_and_remains_in_slot_but_mips_not_safe(self):
        rows=f3.project_capacity(self.pad,self.geo,self.projected)['rows']
        row=next(r for r in rows if r['script_id']==100100)
        self.assertTrue(row['would_fit_existing_block_allocation'])
        self.assertEqual(row['net_spanish_text_delta_bytes'],-1)
        self.assertEqual(row['hypothetical_internal_command_start_changes'],268)
        self.assertFalse(row['model_internal_offsets_not_shifted'])

    def test_100101_padding_13_and_delta_115(self):
        rows=f3.project_capacity(self.pad,self.geo,self.projected)['rows']
        row=next(r for r in rows if r['script_id']==100101)
        self.assertEqual(row['original_zero_tail_bytes'],13)
        self.assertEqual(row['minimum_additional_capacity_bytes_if_individually_aligned'],112)

    def test_small_overflow_still_requires_alignment(self):
        rows=f3.project_capacity(self.pad,self.geo,self.projected)['rows']
        row=next(r for r in rows if r['script_id']==100120)
        self.assertEqual(row['net_spanish_text_delta_bytes'],2)
        self.assertEqual(row['original_zero_tail_bytes'],1)
        self.assertEqual(row['minimum_additional_capacity_bytes_if_individually_aligned'],16)

    def test_sha_tampering_fails_closed(self):
        bad=copy.deepcopy(self.pad);bad['script_tbl_sha256']='0'*64
        with self.assertRaises(ValueError):f3.validate_padding(bad,self.geo)

    def test_padding_tampering_fails_closed(self):
        bad=copy.deepcopy(self.pad);bad['padding_rows'][3][5]+=1
        with self.assertRaises(ValueError):f3.validate_padding(bad,self.geo)

    def test_source_end_tampering_fails_closed(self):
        bad=copy.deepcopy(self.pad);bad['padding_rows'][0][3]+=16
        with self.assertRaises(ValueError):f3.validate_padding(bad,self.geo)

    def test_block_duplicate_fails_closed(self):
        bad=copy.deepcopy(self.pad);bad['padding_rows'][1]=bad['padding_rows'][0][:]
        with self.assertRaises(ValueError):f3.validate_padding(bad,self.geo)

    def test_plan_duplicate_or_missing_fails_closed(self):
        bad=self.projected[:-1]+[self.projected[0]]
        with self.assertRaises(ValueError):f3.project_capacity(self.pad,self.geo,bad)

    def test_source_commands_mismatch_fails_closed(self):
        bad=copy.deepcopy(self.projected);bad[3]['source_commands']+=1
        with self.assertRaises(ValueError):f3.project_capacity(self.pad,self.geo,bad)

    def test_positive_delta_but_changed_canonical_totals_rejected(self):
        bad=copy.deepcopy(self.projected);bad[3]['net_text_byte_delta']+=1
        with self.assertRaises(ValueError):f3.project_capacity(self.pad,self.geo,bad)

    def test_reject_negative_eliminating_all_commands(self):
        bad=copy.deepcopy(self.projected);bad[0]['net_text_byte_delta']=-100000
        with self.assertRaises(ValueError):f3.project_capacity(self.pad,self.geo,bad,canonical=False)

    def test_no_published_payload_strings(self):
        self.assertNotIn('original_text_bytes_hex',self.pad)
        self.assertFalse(f3.project_capacity(self.pad,self.geo,self.projected)['relocation_authorized'])

class TestRealDraftInCI(unittest.TestCase):
    def test_real_9237_record_draft_budget(self):
        r=f3.audit(ROOT/f3.anchor.DRAFT_REL,ROOT/f3.anchor.GEOMETRY_REL,ROOT/f3.PADDING_REL)
        self.assertEqual(r['corpus_rows'],9237)
        self.assertEqual(r['blocked_variable_length'],85)
        self.assertEqual(r['totals']['min_additional_capacity_if_each_block_individually_16_aligned'],144)
        self.assertEqual(r['totals']['hypothetical_internal_command_start_changes'],588)
        self.assertIsNone(r['iso_verification'])
        self.assertFalse(r['relocation_authorized'])

if __name__=='__main__':unittest.main()
