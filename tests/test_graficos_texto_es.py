#!/usr/bin/env python3
"""Graphical text isolation tests with synthetic PNGs, no copyrighted assets."""
import struct
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from PIL import Image
from graficos_texto_es import GRAPHICS, DIMENSIONS, verify_outside_roi, mask_pixels
from integrar_parche_seguro import rebuild_sys_arc
from extract_cladun import dsarc_entries

PNG_SIG = bytes.fromhex("89504E470D0A1A0A")


class TestGraphicsIsolation(unittest.TestCase):
    def test_exactly_six_expected_text_images_and_rois(self):
        self.assertEqual(set(GRAPHICS), {
            "PIC1.PNG", "DOT_PIC1.PNG", "SAVE.PNG", "DOT_SAVE.PNG",
            "NODATA.PNG", "DOT_NODATA.PNG"})
        for name, (sha, roi, size, label, color) in GRAPHICS.items():
            self.assertEqual(len(sha), 64)
            self.assertTrue(all(0 <= n <= m for n, m in zip(roi, (DIMENSIONS[name][0],
                             DIMENSIONS[name][1], DIMENSIONS[name][0], DIMENSIONS[name][1]))))
            self.assertTrue(label)

    def test_reject_pixel_change_outside_text_roi(self):
        left = Image.new("RGB", (40, 20), (90, 90, 90))
        right = left.copy()
        right.putpixel((14, 7), (255, 255, 255))
        self.assertTrue(verify_outside_roi(left, right, (10, 5, 20, 12)))
        right.putpixel((25, 7), (255, 0, 0))
        with self.assertRaises(ValueError):
            verify_outside_roi(left, right, (10, 5, 20, 12))

    def test_mask_never_escapes_text_roi(self):
        image = Image.new("RGB", (144, 80), (48, 48, 48))
        for x in range(30, 38):
            image.putpixel((x, 37), (186, 105, 19))
        roi = (20, 29, 126, 56)
        mask = mask_pixels("NODATA.PNG", image, roi)
        self.assertTrue(mask)
        self.assertTrue(all(roi[0] <= x < roi[2] and roi[1] <= y < roi[3]
                            for x, y in mask))

    def test_appended_graphics_keep_old_png_bytes_unchanged(self):
        archive = bytearray(4096)
        archive[:8] = b"DSARC FL"
        struct.pack_into("<I", archive, 8, 6)
        records = {}
        for i, name in enumerate(GRAPHICS):
            at = 16 + i * 48
            archive[at:at + len(name)] = name.encode("ascii")
            offset = 512 + i * 512
            original = PNG_SIG + bytes([i]) * 9
            archive[offset:offset + len(original)] = original
            struct.pack_into("<II", archive, at + 40, len(original), offset)
            text = GRAPHICS[name][3]
            records[name] = [({"grupo_id": str(i), "tipo": (
                "mensaje_grafico" if "NODATA" in name else "titulo_grafico"),
                "origen": "SYS.DAT2/" + name,
                "original": "NO DATA" if "NODATA" in name else "This is an RPG!"},
                b"", text.encode("utf-8"))]

        def fake_patch(name, value, translated):
            self.assertTrue(value.startswith(PNG_SIG))
            return PNG_SIG + b"TranslatedBytes", {"asset": name}

        with patch("integrar_parche_seguro.patch_png", side_effect=fake_patch):
            result, used, audits = rebuild_sys_arc(bytes(archive), records)
        self.assertEqual(len(used), 6)
        self.assertEqual(len(audits), 6)
        after = dsarc_entries(result)
        for item in after:
            self.assertGreaterEqual(item["offset"], len(archive))
            self.assertTrue(result[item["offset"]:item["offset"] + item["size"]].startswith(PNG_SIG))
        self.assertEqual(result[512:4096], bytes(archive[512:4096]))

    def test_missing_graphic_is_rejected(self):
        archive = bytearray(512)
        archive[:8] = b"DSARC FL"
        struct.pack_into("<I", archive, 8, 0)
        with self.assertRaises(ValueError):
            rebuild_sys_arc(bytes(archive), {"PIC1.PNG": []})


if __name__ == "__main__":
    unittest.main()
