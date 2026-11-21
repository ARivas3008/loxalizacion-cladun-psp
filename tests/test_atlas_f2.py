"""F2 safeguards: synthetic index table, no game bytes or game assets."""
from pathlib import Path
import sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from generar_probe_f2_indice import build,code_of,get_probe_indices
from charset_es import ES_BYTES,ES_GLYPHS

class TestF2Atlas(unittest.TestCase):
    def setUp(self):
        self.old=list(range(32,127))+list(range(0x8100,0x8100+2721-95))
        self.new=self.old[:95]+list(range(0xA1,0xB4))+self.old[95:]
    def test_old_vs_new_index_moves_19_only_after_ascii(self):
        old=get_probe_indices(self.old,self.new,"old")
        new=get_probe_indices(self.old,self.new,"new")
        for sym in "□○×△":
            self.assertEqual(new[sym],old[sym]+19)
        for sym in "CLR":
            self.assertEqual(new[sym],old[sym])
        self.assertEqual(len(set(new.values())),7)
    def test_cp932_symbols(self):
        self.assertEqual({x:hex(code_of(x)) for x in "□○×△"},
                         {"□":"0x81a0","○":"0x819b","×":"0x817e","△":"0x81a2"})
    def test_19_spanish_single_byte(self):
        self.assertEqual(len(ES_GLYPHS),19)
        self.assertEqual(set(ES_BYTES.values()),{bytes([i]) for i in range(0xA1,0xB4)})
    def test_reject_unknown_font_table(self):
        bad=self.new.copy()
        bad[150]=bad[151]
        with self.assertRaises(AssertionError):
            get_probe_indices(self.old,bad,"new")
    def test_reject_unknown_probe_mode(self):
        with self.assertRaises(ValueError):
            get_probe_indices(self.old,self.new,"invalid")
    def test_reject_bad_iso_hash_before_file_writes(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            fake=directory/"wrong.iso";fake.write_bytes(b"NOT AN ISO")
            candidate=directory/"candidate.iso"
            report=directory/"report.json"
            with self.assertRaises(ValueError):
                build(fake,candidate,report,mode="old")
            self.assertFalse(candidate.exists())
            self.assertFalse(report.exists())

if __name__=="__main__":unittest.main()
