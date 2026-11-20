#!/usr/bin/env python3
"""Pruebas de aislamiento entre las dos localizaciones."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from auditar_referencia_la_pucelle import auditar, leer


class ReferenciaLaPucelleTest(unittest.TestCase):
    def test_snapshot_y_glosario_local_presentes(self):
        ref = leer(ROOT / "referencias/la_pucelle/terminos_investigados.csv")
        loc = leer(ROOT / "traduccion/GLOSARIO_CANONICO.csv")
        self.assertEqual(len(ref), 36)
        self.assertEqual(len(loc), 67)
        result = auditar(ref, loc)
        self.assertEqual(result["terminos_importados_automaticamente"], 0)
        self.assertFalse(result["glosario_cladun_modificado"])
        self.assertEqual(result["sin_resolver_pucelle"], 1)

    def test_no_confundir_espanol_igual_con_termino_ingles(self):
        ref = [{"termino": "魔界", "nombre_ingles": "Dark World",
                "espanol": "Mundo Oscuro", "confianza": "Alta",
                "estatus": "validacion", "fuente_url": "", "nota": ""}]
        loc = [{"original": "Other World", "espanol": "Mundo Oscuro",
                "estado": "pendiente"}]
        self.assertEqual(auditar(ref, loc)["coincidencias_exactas_original_o_ingles"], 0)

    def test_coincidencia_explicita_pide_revision(self):
        ref = [{"termino": "魔界", "nombre_ingles": "Dark World",
                "espanol": "Mundo Oscuro", "confianza": "Alta",
                "estatus": "validacion", "fuente_url": "", "nota": ""}]
        loc = [{"original": "dark world", "espanol": "Otro mundo",
                "estado": "pendiente"}]
        result = auditar(ref, loc)
        self.assertEqual(result["coincidencias_exactas_original_o_ingles"], 1)
        self.assertEqual(result["coincidencias"][0]["equivalencia"],
                         "traduccion_distinta_requiere_contexto")

    def test_no_transferir_cadena_sin_resolver(self):
        ref = [{"termino": "ェD", "nombre_ingles": "Unknown", "espanol": "[SIN RESOLVER]",
                "confianza": "Sin resolver", "estatus": "pendiente",
                "fuente_url": "", "nota": ""}]
        loc = [{"original": "Unknown", "espanol": "Desconocido", "estado": "pendiente"}]
        self.assertEqual(auditar(ref, loc)["coincidencias_exactas_original_o_ingles"], 0)


if __name__ == "__main__":
    unittest.main()
