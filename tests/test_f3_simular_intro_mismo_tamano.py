"""F3: solo tests B sintéticos + borrador Git real; sin ISO comercial en CI."""
from __future__ import annotations
import copy
import struct
import unittest
from pathlib import Path
from tools import f3_simular_intro_mismo_tamano as f3
from tools import f3_anclar_intro as anchor


ROOT=Path(__file__).resolve().parents[1]


def sample():
    raw=b'ABC'
    block={'block_index':0,'script_id':100100,'name':'demo1001_00.dsf',
           'command_count':1,'source_start':0,'source_end':16}
    span={'offset':7,'script_id':100100,'script_file':'demo1001_00.dsf',
          'block_index':0,'command_order':0,'source_length':3,'following_commands':0}
    geo={'schema':'cladun.f3.intro_source_geometry.v2','blocks':[block],
         'text_spans':[span],
         'source_and_order_sha256':anchor.anchor_hash([(span,raw)])}
    row={'grupo_id':'7','origen':'SCRIPT.SDT/SCRIPT.DAT',
         'script':'demo1001_00.dsf','script_id':'100100','offset_hex':'0x7',
         'bytes_hex':raw.hex(),'longitud_original_bytes':'3',
         'original':'ABC','espanol':'BBB'}
    # One text command followed by zero padding; 1624 empty script blocks.
    command=bytes([0x66])+struct.pack('<HHH',13,6,3)+raw+b'\0'
    assert len(command)==11
    data=command+b'\0'*5
    table=bytearray(16+1625*32)
    struct.pack_into('<I',table,0,1625)
    for i in range(1625):
        struct.pack_into('<I',table,16+i*32+4,0 if i==0 else16)
    return [row],geo,data,bytes(table)


class TestPlans(unittest.TestCase):
    def test_exact_same_length_is_selected(self):
        rows,geo,_,_=sample()
        plan,stats=f3.prepare_plan(rows,geo,canonical=False)
        self.assertEqual(len(plan),1)
        self.assertEqual((plan[0]['old'],plan[0]['new']),(b'ABC',b'BBB'))
        self.assertEqual(stats['change_counts'],{'same_length_changed':1})

    def test_unequal_length_is_not_selected(self):
        rows,geo,_,_=sample();rows[0]['espanol']='LONGER'
        plan,stats=f3.prepare_plan(rows,geo,canonical=False)
        self.assertEqual(plan,[])
        self.assertEqual(stats['change_counts'],{'unequal':1})

    def test_unchanged_is_not_selected(self):
        rows,geo,_,_=sample();rows[0]['espanol']='ABC'
        plan,stats=f3.prepare_plan(rows,geo,canonical=False)
        self.assertEqual(plan,[])
        self.assertEqual(stats['change_counts'],{'unchanged':1})

    def test_source_anchor_mismatch_rejected(self):
        rows,geo,_,_=sample();rows[0]['bytes_hex']='414244'
        rows[0]['original']='ABD'
        with self.assertRaises(ValueError):f3.prepare_plan(rows,geo,canonical=False)

    def test_wrong_script_block_rejected(self):
        rows,geo,_,_=sample();rows[0]['script_id']='999'
        with self.assertRaises(ValueError):f3.prepare_plan(rows,geo,canonical=False)

    def test_invalid_spanish_character_rejected(self):
        rows,geo,_,_=sample();rows[0]['espanol']='🙂'
        with self.assertRaises(UnicodeEncodeError):
            f3.prepare_plan(rows,geo,canonical=False)

    def test_no_unauthorized_extra_row(self):
        rows,geo,_,_=sample();rows.append(dict(rows[0]))
        with self.assertRaises(ValueError):f3.prepare_plan(rows,geo,canonical=False)


class TestMemoryOnly(unittest.TestCase):
    def test_full_script_table_and_offsets_preserved(self):
        rows,geo,data,table=sample()
        plan,_=f3.prepare_plan(rows,geo,canonical=False)
        result=f3.simulate_memory_only(data,table,geo,plan,expected_commands=1)
        self.assertEqual(result['equal_length_text_candidates_simulated'],1)
        self.assertEqual(result['changed_payload_bytes'],2)
        self.assertTrue(result['all_command_offsets_preserved'])
        self.assertEqual(result['original_script_blocks'],1625)
        self.assertEqual(result['moved_script_starts'],0)
        self.assertEqual(result['virtual_bytes'],len(data))
        self.assertNotEqual(result['virtual_script_dat_sha256_NOT_A_FILE'],result['original_script_dat_sha256'])
        self.assertFalse(result['integration_authorized'])
        self.assertFalse(result['MIPS_jumps_and_external_references_verified'])
        self.assertFalse(result['new_ISO_created'])

    def test_original_source_byte_mutation_is_rejected(self):
        rows,geo,data,table=sample();plan,_=f3.prepare_plan(rows,geo,canonical=False)
        wrong=bytearray(data);wrong[7]=ord('Z')
        with self.assertRaises(ValueError):
            f3.simulate_memory_only(bytes(wrong),table,geo,plan,expected_commands=1)

    def test_length_changing_plan_is_rejected(self):
        rows,geo,data,table=sample();plan,_=f3.prepare_plan(rows,geo,canonical=False)
        wrong=copy.deepcopy(plan);wrong[0]['new']=b'TOO_LONG'
        with self.assertRaises(ValueError):
            f3.simulate_memory_only(data,table,geo,wrong,expected_commands=1)

    def test_unrecognized_text_slot_is_rejected(self):
        rows,geo,data,table=sample();plan,_=f3.prepare_plan(rows,geo,canonical=False)
        wrong=copy.deepcopy(plan);wrong[0]['offset']=8
        with self.assertRaises(ValueError):
            f3.simulate_memory_only(data,table,geo,wrong,expected_commands=1)

    def test_overlapping_or_duplicate_changes_rejected(self):
        rows,geo,data,table=sample();plan,_=f3.prepare_plan(rows,geo,canonical=False)
        with self.assertRaises(ValueError):
            f3.simulate_memory_only(data,table,geo,plan+plan,expected_commands=1)

    def test_absent_text_changes_does_not_claim_gameplay(self):
        rows,geo,data,table=sample()
        r=f3.simulate_memory_only(data,table,geo,[],expected_commands=1)
        self.assertEqual(r['text_commands_replaced'] if 'text_commands_replaced' in r else
                         r['equal_length_text_candidates_simulated'],0)
        self.assertFalse(r['PPSSPP_executed'])
        self.assertFalse(r['integration_authorized'])

    def test_incorrect_command_count_rejected(self):
        rows,geo,data,table=sample();plan,_=f3.prepare_plan(rows,geo,canonical=False)
        with self.assertRaises(ValueError):
            f3.simulate_memory_only(data,table,geo,plan,expected_commands=51705)


class TestAuthenticDraftInCI(unittest.TestCase):
    def test_canonical_9237_row_draft_has_exactly_11_candidates(self):
        report=f3.audit(ROOT/anchor.DRAFT_REL, ROOT/anchor.GEOMETRY_REL)
        self.assertEqual(report['intro_original_text_rows'],97)
        self.assertEqual(report['same_length_candidates'],11)
        self.assertEqual(report['changed_length_blocked'],85)
        self.assertEqual(report['unchanged_intro_fields'],1)
        self.assertFalse(report['iso_original_reverified_this_call'])
        self.assertFalse(report['script_in_memory_simulation_executed'])
        self.assertFalse(report['deployment_authorized'])


if __name__=='__main__': unittest.main()
