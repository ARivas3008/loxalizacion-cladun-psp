#!/usr/bin/env python3
"""Fixtures sintéticos exclusivamente para testear el analizador; nunca evidencia de PPSSPP."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from medir_f1_ppsspp import measure_options, analyze_manifest


class TestMedidorF1(unittest.TestCase):
    def test_ancho_756_y_residuo_16_sobre_fixture_sintetico(self):
        im = Image.new("RGB", (1280,720), color=(0,0,0))
        ImageDraw.Draw(im).line((342,106,1097,106), fill=(255,255,255))
        measured = measure_options(im)
        self.assertEqual(measured["interior_px"], 756)
        self.assertEqual(measured["exterior_estimado_px"], 764)
        ImageDraw.Draw(im).line((342,106,357,106), fill=(0,0,0))
        self.assertEqual(measure_options(im)["interior_px"], 740)
        self.assertEqual(measure_options(im)["exterior_estimado_px"], 748)

    def test_rechaza_resolucion_distinta(self):
        with self.assertRaises(ValueError):
            measure_options(Image.new("RGB", (960,544)))

    def test_png_real_en_formato_pero_origen_no_validable(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            im = Image.new("RGB", (1280,720))
            ImageDraw.Draw(im).line((358,106,1097,106), fill=(255,255,255))
            img = tmp/"fixture-sintetico.png"
            im.save(img)
            digest = hashlib.sha256(img.read_bytes()).hexdigest()
            manifest = tmp/"manifest.json"
            base = {"ruta":str(img), "pantalla":"Opciones", "version":"TEST_SINTETICO",
                    "sha256_esperado":digest}
            manifest.write_text(json.dumps({"schema":"cladun.f1.ppsspp_png_inputs.v1",
                "origen":"TEST_SINTETICO_NO_PPSSPP",
                "capturas":[{**base,"estado":"primer_estado"},
                            {**base,"estado":"segundo_estado"}]}),encoding="utf-8")
            data = analyze_manifest(manifest, require_two_states=True)
            self.assertEqual(data["cantidad_capturas_png"],2)
            self.assertIn("NO_CERTIFICAN",data["estado"])
            self.assertEqual(data["capturas"][0]["medicion"]["interior_px"],740)
            manifest.write_text(manifest.read_text().replace(digest, "0"*64),
                                encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                analyze_manifest(manifest,require_two_states=True)

    def test_exige_dos_estados_por_pantalla(self):
        with tempfile.TemporaryDirectory() as d:
            tmp=Path(d)
            image=tmp/"fixture-sintetico.png"
            Image.new("RGB",(1280,720)).save(image)
            mani=tmp/"m.json"
            mani.write_text(json.dumps({"schema":"cladun.f1.ppsspp_png_inputs.v1",
                "capturas":[{"ruta":str(image),"pantalla":"Controles",
                             "version":"TEST_SINTETICO","estado":"uno"}]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Faltan dos estados"):
                analyze_manifest(mani,require_two_states=True)


if __name__=="__main__":
    unittest.main()
