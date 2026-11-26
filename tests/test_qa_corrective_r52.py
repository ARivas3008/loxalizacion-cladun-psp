import unittest
from tools.qa_corrective_r52 import save_overlay,verify_ink_delta,font_metrics,advance,wrap_plain,RESOURCE
from tools.qa_corrective_r52 import compact_menu_overlay,COMPACT,MENU
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

class CorrectiveTests(unittest.TestCase):
    def test_save_scoped(self):
        s={'origen':RESOURCE,'indice_registro':'34','offset_hex':'0xcc8','original':'Save','bytes_hex':'53617665','grupo_id':'x'}
        d={**s,'espanol':'Ahorrar'}; other={**s,'indice_registro':'35'}
        rows,log=save_overlay([(s,d),(other,d)])
        self.assertEqual(rows[0][1]['espanol'],'Guardar');self.assertEqual(rows[1][1]['espanol'],'Ahorrar')
        self.assertEqual(d['espanol'],'Ahorrar');self.assertEqual(log['id'],'x')
        with self.assertRaises(ValueError):save_overlay([({**s,'offset_hex':'0xcc9'},d)])
        with self.assertRaises(ValueError):save_overlay([])
        with self.assertRaises(ValueError):save_overlay([(s,{**d,'espanol':'Otro'})])
    def test_compact_scope(self):
        pairs=[]
        for idx,(gid,before,after,*_) in COMPACT.items():
            off,orig=MENU[idx]
            s={'origen':RESOURCE,'indice_registro':str(idx),'offset_hex':hex(off),'original':orig,'bytes_hex':orig.encode().hex(),'grupo_id':gid}
            pairs.append((s,{**s,'espanol':before}))
        extra={**pairs[1][0],'indice_registro':'421'}
        pairs.append((extra,{**extra,'espanol':'Creación de personajes'}))
        result,log=compact_menu_overlay(pairs)
        self.assertEqual([d['espanol'] for _,d in result],['Círculo/Equipar','Crear personajes','Color','Creación de personajes'])
        self.assertEqual(len(log),3)
        self.assertTrue(all(r['after_px']<=r['original_px'] for r in log))
        with self.assertRaises(ValueError):compact_menu_overlay(pairs[1:])
    def test_ink_guard(self):
        old=[bytes(256)]*3072;old[95]=bytes([15]*100+[0]*156);old[0]=bytes([15]*256)
        new=old.copy();new[95]=bytes([1]*100+[0]*156)
        self.assertEqual(verify_ink_delta(old,new),100)
        with self.assertRaises(ValueError):verify_ink_delta(old,old)
        new[0]=bytes([1]*256)
        with self.assertRaises(ValueError):verify_ink_delta(old,new)
    def test_width_wrap(self):
        w={'a':7,'i':3,' ':7,'b':7};self.assertEqual(advance('ai',w),10)
        self.assertEqual(wrap_plain('ai bb',w,14,2),['ai','bb'])
        for s in ('ai\nbb','ai %d','ai  bb','bbbb','ai bb ai'):
            with self.assertRaises(ValueError):wrap_plain(s,w,14,2)
        with self.assertRaises(ValueError):advance('ñ',w)
    def test_font_table(self):
        b=struct.pack('<IHBBHBB',2,32,0,7,65,0,8)
        self.assertEqual(font_metrics(b),{32:7,65:8})
        with self.assertRaises(ValueError):font_metrics(b[:-1])

    def test_real_corpus_plan_scope(self):
        from tools.integrar_parche_seguro import source_rows,plan_rows
        rows=source_rows()
        before,bb,bu=plan_rows(rows)
        rows,_=save_overlay(rows)
        rows,_=compact_menu_overlay(rows)
        after,ab,au=plan_rows(rows)
        self.assertEqual((bb,bu),(ab,au))
        def flatten(d):
            return {s['grupo_id']:(resource,old,new) for resource,items in d.items() for s,old,new in items}
        a,b=flatten(before),flatten(after)
        self.assertEqual(set(a),set(b))
        self.assertEqual({k for k in a if a[k]!=b[k]}, {'005234','005236','005237','005242'})
        self.assertTrue(all(a[k][:2]==b[k][:2] for k in a))

if __name__=='__main__':unittest.main()
