"""Únicamente PNG y manifiestos SINTÉTICOS; no se ejecuta PPSSPP en CI."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import f2_cotejar_capturas_tuika as mod


def sha(data):
    return hashlib.sha256(data).hexdigest()


def make_manifest(folder, scene='CONTROLES', version='v1.20.4', title='Cladun: This Is an RPG!', change=False):
    folder.mkdir(parents=True, exist_ok=True)
    shots=[]
    for n in (1, 2):
        im=Image.new('RGB', (6, 4), (249, 251, 249))
        if change:
            im.putpixel((1, 2), (255, 0, 255))
        path=folder / f'{scene}_{n:02d}.png'
        im.save(path)
        data=path.read_bytes()
        shots.append({'name':path.name,'bytes':len(data),'sha256':sha(data),
                      'psp_framebuffer_width':6,'psp_framebuffer_height':4,
                      'emulated_ticks_at_pause':100*n})
    manifest={'schema':mod.MANIFEST_SCHEMA,'ppsspp':version,'game':{'title':title},
              'scene':scene,'captures':{
              'source':'gpu.buffer.screenshot on paused PSP emulator (not desktop window)',
              'screenshots':shots}}
    p=folder/'manifest_PRIVATE.json'
    p.write_text(json.dumps(manifest), encoding='utf-8')
    return p


class TestStaticPair(unittest.TestCase):
    def test_one_magenta_diagnostic_candidate(self):
        a=Image.new('RGB',(3,2),(249,251,249))
        b=a.copy();b.putpixel((1,1),(255,0,255))
        r=mod.compare_pair(a,b)
        self.assertEqual(r['candidate_new_magenta_pixels'],1)
        self.assertEqual(r['different_pixels'],1)
        self.assertEqual(r['candidate_magenta_bbox_inclusive'],[1,1,1,1])
        self.assertTrue(r['manual_scene_alignment_required'])
    def test_no_magenta_never_proves_unused(self):
        a=Image.new('RGB',(4,4),(0,0,0))
        r=mod.compare_pair(a,a.copy())
        self.assertEqual(r['candidate_new_magenta_pixels'],0)
        self.assertTrue(r['zero_magenta_does_not_disprove_texture_usage'])
    def test_other_color_diffs_not_diagnostic(self):
        a=Image.new('RGB',(3,2),(0,0,0))
        b=a.copy(); b.putpixel((1,1),(200,100,180))
        self.assertEqual(mod.compare_pair(a,b)['candidate_new_magenta_pixels'],0)
    def test_existing_magenta_not_new(self):
        a=Image.new('RGB',(3,2),(255,0,255))
        b=a.copy();b.putpixel((1,1),(250,10,240))
        self.assertEqual(mod.compare_pair(a,b)['candidate_new_magenta_pixels'],0)
    def test_size_mismatch_refused(self):
        with self.assertRaises(ValueError):
            mod.compare_pair(Image.new('RGB',(3,2)),Image.new('RGB',(4,2)))
    def test_non_rgb_refused(self):
        with self.assertRaises(ValueError):
            mod.compare_pair(Image.new('RGBA',(3,2)),Image.new('RGB',(3,2)))

class TestCaptureManifest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.repo=self.root/'faux_checkout';self.repo.mkdir()
        self.folder=self.root/'private'
        self.manifest=make_manifest(self.folder)
    def test_two_files_verified_and_declared_only(self):
        r=mod.load_capture(self.manifest,self.repo)
        self.assertEqual(len(r['frames']),2)
        self.assertEqual(r['dimensions'],[[6,4],[6,4]])
        self.assertTrue(r['capture_times_advance'])
    def test_tampered_png_rejected(self):
        p=self.folder/'CONTROLES_01.png'
        with p.open('ab') as f:f.write(b'x')
        with self.assertRaises(ValueError):mod.load_capture(self.manifest,self.repo)
    def test_unsupported_version(self):
        x=json.loads(self.manifest.read_text());x['ppsspp']='v1.20.3'
        self.manifest.write_text(json.dumps(x))
        with self.assertRaises(ValueError):mod.load_capture(self.manifest,self.repo)
    def test_wrong_game(self):
        x=json.loads(self.manifest.read_text());x['game']['title']='Other RPG'
        self.manifest.write_text(json.dumps(x))
        with self.assertRaises(ValueError):mod.load_capture(self.manifest,self.repo)
    def test_shots_count_strict(self):
        x=json.loads(self.manifest.read_text());x['captures']['screenshots'].pop()
        self.manifest.write_text(json.dumps(x))
        with self.assertRaises(ValueError):mod.load_capture(self.manifest,self.repo)
    def test_shot_path_traversal_refused(self):
        x=json.loads(self.manifest.read_text());x['captures']['screenshots'][0]['name']='../../secret.png'
        self.manifest.write_text(json.dumps(x))
        with self.assertRaises(ValueError):mod.load_capture(self.manifest,self.repo)
    def test_fake_framebuffer_size_refused(self):
        x=json.loads(self.manifest.read_text());x['captures']['screenshots'][0]['psp_framebuffer_width']=480
        self.manifest.write_text(json.dumps(x))
        with self.assertRaises(ValueError):mod.load_capture(self.manifest,self.repo)
    def test_symlink_png_refused(self):
        src=self.folder/'CONTROLES_01.png';tmp=self.root/'original.png'
        src.rename(tmp);src.symlink_to(tmp)
        with self.assertRaises(ValueError):mod.load_capture(self.manifest,self.repo)
    def test_private_report_cannot_live_inside_checkout(self):
        with self.assertRaises(ValueError):mod.private_path(self.repo/'private.json',self.repo,for_output=True)
    def test_private_report_cannot_overwrite(self):
        with self.assertRaises(ValueError):mod.private_path(self.manifest,self.repo,for_output=True)
    def test_nonabsolute_refused(self):
        with self.assertRaises(ValueError):mod.private_path(Path('private.json'),self.repo,for_output=True)

class TestABReport(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.repo=self.root/'checkout';self.repo.mkdir()
        self.a=make_manifest(self.root/'A')
        self.b=make_manifest(self.root/'B',change=True)
        self.isoa=self.root/'A.iso';self.isob=self.root/'B.iso'
        self.isoa.write_bytes(b'USA_SYNTHETIC');self.isob.write_bytes(b'PROBE_SYNTHETIC')
        self.patches=[patch.object(mod,'ISO_SIZE',len(b'USA_SYNTHETIC')),
                      patch.object(mod,'USA_SHA',sha(b'USA_SYNTHETIC')),
                      patch.object(mod,'PROBE_SHA',sha(b'PROBE_SYNTHETIC'))]
        # Equal synthetic lengths to match strict size invariant.
        self.isob.write_bytes(b'PROBE_SYNTHET')
        self.patches[2]=patch.object(mod,'PROBE_SHA',sha(b'PROBE_SYNTHET'))
        for pp in self.patches:pp.start();self.addCleanup(pp.stop)
        self.out=self.root/'result.json'
    def test_full_synthetic_report_does_not_claim_runtime_identity(self):
        r=mod.audit(self.a,self.b,self.isoa,self.isob,self.out,self.repo)
        self.assertEqual([p['candidate_new_magenta_pixels'] for p in r['pairs']],[1,1])
        self.assertFalse(r['runtime_loaded_iso_identity_proven'])
        self.assertFalse(r['tuika_texture_runtime_origin_proven'])
        self.assertFalse(r['mips_ram_ge_vram_pipeline_proven'])
        self.assertFalse(r['graphics_or_png_embedded_in_report'])
        self.assertTrue(self.out.exists())
    def test_discordant_scenes_refused(self):
        x=json.loads(self.b.read_text());x['scene']='COMBATE'
        self.b.write_text(json.dumps(x))
        with self.assertRaises(ValueError):mod.audit(self.a,self.b,self.isoa,self.isob,self.out,self.repo)
    def test_modified_probe_iso_rejected(self):
        self.isob.write_bytes(b'NONINTEGRITY')
        with self.assertRaises(ValueError):mod.audit(self.a,self.b,self.isoa,self.isob,self.out,self.repo)
    def test_existing_report_never_overwritten(self):
        self.out.write_text('keep')
        with self.assertRaises(ValueError):mod.audit(self.a,self.b,self.isoa,self.isob,self.out,self.repo)
        self.assertEqual(self.out.read_text(),'keep')

if __name__=='__main__':unittest.main()
