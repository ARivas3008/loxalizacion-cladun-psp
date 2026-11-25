"""B: tests sintéticos X11 A/B/A; NO son capturas del juego ni PPSSPP."""
from __future__ import annotations
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import f2_cotejar_x11_aba as mod

def sha(data):return hashlib.sha256(data).hexdigest()

def manifest(folder:Path,role:str,pid:int,color=(249,251,249)):
    folder.mkdir(parents=True,exist_ok=True)
    png=folder/'SYNTHETIC.png'
    Image.new('RGB',(960,544),color).save(png)
    data=png.read_bytes()
    v={'schema':mod.x11.SCHEMA,'runtime':'REAL_X11_PPSSPP_1.20.4',
       'source_iso_role':role,
       'source_iso_sha256':mod.x11.USA_SHA if role=='usa' else mod.x11.PROBE_SHA,
       'x11':{'window_pid':pid,'width':960,'height':544,
              'window_size_960x544':True,'window_title_is_cladun':True},
       'x11_window_pid_correlated_to_procfs':True,
       'paired':{'pid_starttime_stable':True,'same_inode_open_before_and_after':True},
       'screenshot_x11':{'filename':png.name,'sha256':sha(data),'bytes':len(data),
                         'width':960,'height':544},
       'this_is_psp_framebuffer':False,
       'runtime_loaded_iso_identity_proven':False,
       'mips_ram_ge_vram_proven':False}
    path=folder/'witness.json';path.write_text(json.dumps(v));return path

class MetricsB(unittest.TestCase):
    def test_stable_probe_magenta_native_and_animation(self):
        a=Image.new('RGB',(4,2),(249,251,249));b=a.copy();c=a.copy()
        b.putpixel((0,0),(255,0,255))
        for im in (a,b,c):im.putpixel((1,0),(255,0,255))
        a.putpixel((2,0),(10,10,10));b.putpixel((2,0),(255,0,255));c.putpixel((2,0),(20,20,20))
        b.putpixel((3,1),(88,44,99))
        r=mod.metrics(a,b,c)
        self.assertEqual(r['stable_usa_before_after_pixels'],7)
        self.assertEqual(r['unstable_usa_before_after_pixels'],1)
        self.assertEqual(r['candidate_probe_only_changed_on_stable_usa_pixels'],2)
        self.assertEqual(r['candidate_probe_only_new_magenta_on_stable_usa_pixels'],1)
        self.assertEqual(r['native_magenta_on_stable_usa_pixels'],1)
        self.assertEqual(r['ambiguous_pixels_with_reference_variation'],1)
        self.assertEqual(r['probe_only_new_magenta_bbox_inclusive'],[0,0,0,0])
        self.assertFalse(r['texture_gpu_identity_proven'])
    def test_native_magenta_not_new(self):
        a=Image.new('RGB',(3,2),(255,0,255))
        r=mod.metrics(a,a.copy(),a.copy())
        self.assertEqual(r['native_magenta_on_stable_usa_pixels'],6)
        self.assertEqual(r['candidate_probe_only_new_magenta_on_stable_usa_pixels'],0)
    def test_animated_control_not_candidate(self):
        a=Image.new('RGB',(2,2),(0,0,0));b=Image.new('RGB',(2,2),(255,0,255))
        c=Image.new('RGB',(2,2),(1,1,1))
        r=mod.metrics(a,b,c)
        self.assertEqual(r['unstable_usa_before_after_pixels'],4)
        self.assertEqual(r['candidate_probe_only_new_magenta_on_stable_usa_pixels'],0)
    def test_rgb_and_same_dimensions_required(self):
        a=Image.new('RGB',(3,2))
        with self.assertRaises(ValueError):mod.metrics(a,a,Image.new('L',(3,2)))
        with self.assertRaises(ValueError):mod.metrics(a,a,Image.new('RGB',(2,3)))

class AuditB(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.root=Path(temp.name);self.repo=self.root/'repo';self.repo.mkdir()
        self.usa=self.root/'USA.iso';self.probe=self.root/'PROBE.iso'
        self.usa.write_bytes(b'USA_SYNTHETIC');self.probe.write_bytes(b'PROBE_SYNTHET')
        self.assertEqual(self.usa.stat().st_size,self.probe.stat().st_size)
        changes=[patch.object(mod.x11,'USA_SHA',sha(self.usa.read_bytes())),
                 patch.object(mod.x11,'PROBE_SHA',sha(self.probe.read_bytes())),
                 patch.object(mod.x11,'ISO_SIZE',self.usa.stat().st_size)]
        for p in changes:p.start();self.addCleanup(p.stop)
        self.a=manifest(self.root/'A','usa',101)
        self.b=manifest(self.root/'B','sonda',102)
        self.c=manifest(self.root/'C','usa',103)
        self.out=self.root/'result.json'
    def run_audit(self,roi=None):
        return mod.audit(self.a,self.b,self.c,self.usa,self.probe,
                         self.out,self.repo,'COMBAT_SYNTHETIC',roi)
    def edit(self,path,func):
        data=json.loads(path.read_text());func(data);path.write_text(json.dumps(data))
    def pixel(self,path,xy,color):
        png=path.parent/'SYNTHETIC.png'
        im=Image.open(png).convert('RGB');im.putpixel(xy,color);im.save(png)
        blob=png.read_bytes()
        self.edit(path,lambda d:d['screenshot_x11'].update(bytes=len(blob),sha256=sha(blob)))
    def test_complete_three_manifests_with_roi(self):
        self.pixel(self.b,(234,123),(255,0,255))
        r=self.run_audit((220,110,40,40))
        self.assertEqual(r['full_frame']['candidate_probe_only_new_magenta_on_stable_usa_pixels'],1)
        self.assertEqual(r['roi_frame']['candidate_probe_only_new_magenta_on_stable_usa_pixels'],1)
        self.assertEqual(r['roi_xyxy_exclusive'],[220,110,260,150])
        for k in ('same_scene_alignment_verified','same_animation_frame_verified',
                  'gameplay_skill_or_combat_verified','loaded_iso_game_identity_proven',
                  'mips_ram_ge_vram_proven','temporal_consistency_establishes_causality'):
            self.assertFalse(r[k],k)
        self.assertTrue(self.out.exists())
    def test_no_difference_is_negative_control(self):
        r=self.run_audit()
        self.assertEqual(r['full_frame']['candidate_probe_only_changed_on_stable_usa_pixels'],0)
        self.assertIsNone(r['roi_frame'])
    def test_animation_exclusion_in_pipeline(self):
        self.pixel(self.b,(3,3),(255,0,255))
        self.pixel(self.c,(3,3),(100,100,100))
        r=self.run_audit()
        self.assertEqual(r['full_frame']['candidate_probe_only_new_magenta_on_stable_usa_pixels'],0)
        self.assertEqual(r['full_frame']['unstable_usa_before_after_pixels'],1)
    def test_wrong_probe_iso_rejected_without_output(self):
        self.probe.write_bytes(b'X'*self.probe.stat().st_size)
        with self.assertRaises(ValueError):self.run_audit()
        self.assertFalse(self.out.exists())
    def test_png_sha_mismatch_rejected(self):
        with (self.c.parent/'SYNTHETIC.png').open('ab') as f:f.write(b'bad')
        with self.assertRaises(ValueError):self.run_audit()
    def test_three_independent_directories_required(self):
        self.c=self.a
        with self.assertRaises(ValueError):self.run_audit()
    def test_three_distinct_declared_pids_required(self):
        self.edit(self.c,lambda d:d['x11'].update(window_pid=101))
        with self.assertRaises(ValueError):self.run_audit()
    def test_false_psp_framebuffer_claim_rejected(self):
        self.edit(self.c,lambda d:d.update(this_is_psp_framebuffer=True))
        with self.assertRaises(ValueError):self.run_audit()
    def test_report_inside_checkout_rejected(self):
        self.out=self.repo/'result.json'
        with self.assertRaises(ValueError):self.run_audit()
    def test_no_overwrite(self):
        self.out.write_text('DO NOT OVERWRITE')
        with self.assertRaises(ValueError):self.run_audit()
        self.assertEqual(self.out.read_text(),'DO NOT OVERWRITE')
    def test_invalid_roi_and_scene_rejected(self):
        with self.assertRaises(ValueError):self.run_audit((960,0,2,4))
        with self.assertRaises(ValueError):
            mod.audit(self.a,self.b,self.c,self.usa,self.probe,self.out,self.repo,'../../SPOOF')
    def test_missing_third_witness_rejected(self):
        self.c.unlink()
        with self.assertRaises(FileNotFoundError):self.run_audit()

if __name__=='__main__':unittest.main()
