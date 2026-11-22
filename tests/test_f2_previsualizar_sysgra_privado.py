"""Synthetic-only PSP unswizzle, palette and privacy unit tests."""
from pathlib import Path
import tempfile
import unittest
from tools.f2_previsualizar_sysgra_privado import (
    unswizzle_psp, rgba_palette, indexed_rgba_4bpp, verify_private_path
)

def palette16():
    raw=bytearray(98)
    raw[:4]=b"IMY\x00"
    raw[4]=0x60
    for i in range(16):
        raw[32+4*i:36+4*i]=bytes((i,i+1,i+2,255))
    return bytes(raw)

class PreviewTests(unittest.TestCase):
    def test_single_psp_tile_identity(self):
        data=bytes(range(128))
        self.assertEqual(unswizzle_psp(data,16,8),data)
    def test_two_horizontal_tiles(self):
        original=bytes(range(256))
        out=unswizzle_psp(original,32,8)
        self.assertEqual(out[:16],original[:16])
        self.assertEqual(out[16:32],original[128:144])
        self.assertEqual(out[32:48],original[16:32])
    def test_two_vertical_tiles(self):
        original=bytes(range(256))
        self.assertEqual(unswizzle_psp(original,16,16),original)
    def test_reject_stride_not_multiple_16(self):
        with self.assertRaisesRegex(ValueError,"geometry"):
            unswizzle_psp(b"0"*64,8,8)
    def test_reject_height_not_multiple_8(self):
        with self.assertRaisesRegex(ValueError,"geometry"):
            unswizzle_psp(b"0"*128,16,7)
    def test_reject_short_raster(self):
        with self.assertRaisesRegex(ValueError,"length"):
            unswizzle_psp(b"0"*127,16,8)
    def test_palette16_rgba(self):
        x=rgba_palette(palette16())
        self.assertEqual(len(x),16)
        self.assertEqual(x[1],(1,2,3,255))
    def test_palette256_rgba(self):
        x=bytearray(0x422)
        x[:4]=b"IMY\x00";x[4]=0x20
        x[32:36]=b"\x01\x02\x03\xff"
        self.assertEqual(len(rgba_palette(bytes(x))),256)
        self.assertEqual(rgba_palette(bytes(x))[0],(1,2,3,255))
    def test_bad_palette(self):
        with self.assertRaisesRegex(ValueError,"palette"):
            rgba_palette(b"bad")
    def test_nibble_order(self):
        colors=[(i,0,0,255) for i in range(16)]
        raw=b"\x21" * 128
        pixels,w,h=indexed_rgba_4bpp(raw,16,8,colors)
        self.assertEqual((w,h),(32,8))
        self.assertEqual(pixels[0],(1,0,0,255))
        self.assertEqual(pixels[1],(2,0,0,255))
    def test_4bpp_rejects_short_palette(self):
        with self.assertRaisesRegex(ValueError,"palette"):
            indexed_rgba_4bpp(b"\x00"*128,16,8,[(0,0,0,0)]*15)
    def test_private_path_absolute(self):
        with self.assertRaisesRegex(ValueError,"absolute"):
            verify_private_path(Path("preview.png"))
    def test_private_path_extension(self):
        with self.assertRaisesRegex(ValueError,"absolute"):
            verify_private_path(Path("/tmp/preview.json"))
    def test_private_path_rejects_repo(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            with self.assertRaisesRegex(ValueError,"repository"):
                verify_private_path(root/"assets"/"logo.png",source_root=root)
    def test_private_path_allows_external(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);other=root/"out"/"preview.png"
            self.assertEqual(verify_private_path(other,source_root=root/"repo"),other)
    def test_private_path_existing_file(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); target=root/"existing.png";target.write_bytes(b"sentinel")
            with self.assertRaises(FileExistsError):
                verify_private_path(target,source_root=root/"repo")
    def test_private_path_symlink_into_repo(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/"repo").mkdir();(root/"outsider").symlink_to(root/"repo")
            with self.assertRaisesRegex(ValueError,"repository"):
                verify_private_path(root/"outsider"/"atlas.png",source_root=root/"repo")
