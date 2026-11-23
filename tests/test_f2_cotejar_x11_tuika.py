"""Solo ensayos SINTÉTICOS X11 y manifiestos; NO se ejecuta PPSSPP."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import f2_cotejar_x11_tuika as mod


def sha(data):
    return hashlib.sha256(data).hexdigest()


def make_case(folder: Path, role: str, image=None):
    folder.mkdir(parents=True, exist_ok=True)
    png = folder / 'TEST_X11.png'
    (image or Image.new('RGB', (960, 544), (249, 251, 249))).save(png)
    blob = png.read_bytes()
    report = {
        'schema': mod.SCHEMA, 'runtime':'REAL_X11_PPSSPP_1.20.4',
        'source_iso_role': role,
        'source_iso_sha256': {'usa':mod.USA_SHA,'sonda':mod.PROBE_SHA}[role],
        'x11': {'window_pid': 99 if role=='usa' else 100, 'width':960,'height':544,
                'window_size_960x544':True,'window_title_is_cladun':True},
        'x11_window_pid_correlated_to_procfs':True,
        'paired':{'pid_starttime_stable':True,'same_inode_open_before_and_after':True},
        'screenshot_x11':{'filename':png.name,'sha256':sha(blob),'bytes':len(blob),
                          'width':960,'height':544},
        'this_is_psp_framebuffer':False,
        'runtime_loaded_iso_identity_proven':False,
        'mips_ram_ge_vram_proven':False
    }
    path = folder / 'testigo.json'
    path.write_text(json.dumps(report),encoding='utf-8')
    return path


class TestX11AB(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repo = self.root / 'fake_repo'
        self.repo.mkdir()
        self.ua, self.ub = b'USA-DUMMY', b'PROBE-DUM'
        self.iso_a, self.iso_b = self.root/'source.iso', self.root/'probe.iso'
        self.iso_a.write_bytes(self.ua)
        self.iso_b.write_bytes(self.ub)
        self.patches = [patch.object(mod,'USA_SHA',sha(self.ua)),
                        patch.object(mod,'PROBE_SHA',sha(self.ub)),
                        patch.object(mod,'ISO_SIZE',len(self.ua))]
        for p in self.patches:
            p.start();self.addCleanup(p.stop)
        self.a = make_case(self.root/'A','usa')
        self.b = make_case(self.root/'B','sonda')
        self.report = self.root/'result.json'

    def run_audit(self,roi=None):
        return mod.audit(self.a,self.b,self.iso_a,self.iso_b,self.report,
                         self.repo,'HABILIDAD_DECLARADA',roi=roi)

    def edit(self,path,fn):
        data=json.loads(path.read_text());fn(data)
        path.write_text(json.dumps(data),encoding='utf-8')

    def test_one_new_magenta_is_only_candidate(self):
        pic=Image.open(self.root/'B'/'TEST_X11.png').convert('RGB')
        pic.putpixel((312,120),(255,0,255))
        pic.save(self.root/'B'/'TEST_X11.png')
        content=(self.root/'B'/'TEST_X11.png').read_bytes()
        self.edit(self.b,lambda x:x['screenshot_x11'].update(bytes=len(content),sha256=sha(content)))
        r=self.run_audit((300,100,40,40))
        self.assertEqual(r['full_x11_frame']['different_pixels'],1)
        self.assertEqual(r['full_x11_frame']['candidate_new_magenta_pixels'],1)
        self.assertEqual(r['roi_metrics']['different_pixels'],1)
        self.assertEqual(r['roi_xyxy_exclusive'],[300,100,340,140])
        for k in ('visual_scene_alignment_proven','gameplay_event_proven','psp_framebuffer_used',
                  'loaded_iso_identity_proven','tuika_texture_gpu_identity_proven',
                  'mips_ram_ge_vram_pipeline_proven'):
            self.assertFalse(r[k],k)
        self.assertTrue(self.report.is_file())

    def test_zero_difference_does_not_prove_unused_texture(self):
        r=self.run_audit()
        self.assertTrue(r['identical_png_sha256'])
        self.assertEqual(r['full_x11_frame']['different_pixels'],0)
        self.assertTrue(r['full_x11_frame']['zero_magenta_does_not_disprove_texture_usage'])
        self.assertIsNone(r['roi_metrics'])

    def test_tampered_png_rejected(self):
        with (self.root/'B'/'TEST_X11.png').open('ab') as f:f.write(b'oops')
        with self.assertRaises(ValueError):self.run_audit()
        self.assertFalse(self.report.exists())

    def test_wrong_iso_hash_rejected(self):
        self.iso_b.write_bytes(b'CHANGED!!')
        with self.assertRaises(ValueError):self.run_audit()

    def test_non_x11_manifest_rejected(self):
        self.edit(self.b,lambda x:x.update(runtime='REAL_WS_FRAMEBUFFER'))
        with self.assertRaises(ValueError):self.run_audit()

    def test_role_mismatch_rejected(self):
        self.edit(self.a,lambda x:x.update(source_iso_role='sonda'))
        with self.assertRaises(ValueError):self.run_audit()

    def test_unconfirmed_fd_rejected(self):
        self.edit(self.a,lambda x:x['paired'].update(same_inode_open_before_and_after=False))
        with self.assertRaises(ValueError):self.run_audit()

    def test_false_pid_stability_rejected(self):
        self.edit(self.b,lambda x:x['paired'].update(pid_starttime_stable=False))
        with self.assertRaises(ValueError):self.run_audit()

    def test_wrong_png_dimension_rejected(self):
        Image.new('RGB',(480,272)).save(self.root/'B'/'TEST_X11.png')
        content=(self.root/'B'/'TEST_X11.png').read_bytes()
        self.edit(self.b,lambda x:x['screenshot_x11'].update(bytes=len(content),sha256=sha(content)))
        with self.assertRaises(ValueError):self.run_audit()

    def test_png_path_traversal_rejected(self):
        self.edit(self.b,lambda x:x['screenshot_x11'].update(filename='../A/TEST_X11.png'))
        with self.assertRaises(ValueError):self.run_audit()

    def test_symlink_png_rejected(self):
        pic=self.root/'B'/'TEST_X11.png'
        real=self.root/'target.png'
        pic.rename(real)
        pic.symlink_to(real)
        with self.assertRaises(ValueError):self.run_audit()

    def test_invalid_roi_rejected_before_writing(self):
        for r in [(-1,0,1,1),(0,0,961,1),(0,0,1,545),(30,40,0,1),(0,0,True,1)]:
            with self.subTest(r=r),self.assertRaises(ValueError):self.run_audit(r)
        self.assertFalse(self.report.exists())

    def test_report_does_not_overwrite(self):
        self.report.write_text('DO NOT OVERWRITE')
        with self.assertRaises(ValueError):self.run_audit()
        self.assertEqual(self.report.read_text(),'DO NOT OVERWRITE')

    def test_same_directory_manifest_rejected(self):
        old=self.b
        self.b=self.a
        with self.assertRaises(ValueError):self.run_audit()
        self.b=old

    def test_disallowed_scene_label_rejected(self):
        with self.assertRaises(ValueError):mod.audit(self.a,self.b,self.iso_a,self.iso_b,
                                        self.report,self.repo,'../../fake')

    def test_output_inside_repo_rejected(self):
        self.report=self.repo/'should_not_write.json'
        with self.assertRaises(ValueError):self.run_audit()


if __name__=='__main__':
    unittest.main()
