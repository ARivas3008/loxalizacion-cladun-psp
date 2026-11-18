#!/usr/bin/env python3
"""Contratos de reinserción: sin ISO ni datos comerciales."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from auditar_preinsercion_es import check_row
from charset_es import encode_spanish


def pair(en="Hello?", es="¡Hola!", origin="SCRIPT.SDT/SCRIPT.DAT", capacity=""):
    raw = en.encode("cp932")
    base = {
        "grupo_id": "000001", "text_id": "CLD-DEMO", "tipo": "dialogo",
        "campo": "texto", "original": en, "estado": "pendiente_traduccion",
        "revision_fuente": "campo_binario_confirmado", "origen": origin,
        "indice_registro": "", "script": "", "script_id": "",
        "orden_script": "", "offset_hex": "0x00000120",
        "capacidad_campo": capacity, "longitud_original_bytes": str(len(raw)),
        "bytes_hex": raw.hex().upper(), "idioma_origen": "ingles_o_simbolos",
        "comentario": "",
    }
    translated = {**base, "espanol": es, "revision_es": "posteditado_contextualmente_por_IA"}
    return base, translated


class TestPreinsercion(unittest.TestCase):
    def test_script_rechaza_ampliacion_aun_si_hay_espacio_en_iso(self):
        a, b = pair("Yes", "¿Sí?")
        self.assertEqual(check_row(a, b)["estado"], "BLOQUEADO_CAMBIO_LONGITUD_SCRIPT")

    def test_script_igual_bytes_solo_candidato_no_aprobado(self):
        a, b = pair("Hello?", "Adiós!")  # 6 frente a 7 bytes por ó -> no pasa
        self.assertEqual(check_row(a, b)["estado"], "BLOQUEADO_CAMBIO_LONGITUD_SCRIPT")
        b["espanol"] = "¡Sí!"  # 6 bytes con signos y letra PUA
        self.assertEqual(len(encode_spanish(b["espanol"])), 6)
        out = check_row(a, b)
        self.assertEqual(out["estado"], "CANDIDATO_A_ENSAYO_NO_VALIDADO")
        self.assertFalse(out["aprobado_para_insertar"])

    def test_rechaza_cambio_identidad_origen(self):
        a, b = pair()
        b["original"] = "Cambio!"
        self.assertEqual(check_row(a, b)["estado"], "BLOQUEADO_FUENTE_MODIFICADA")

    def test_campo_fijo_rechaza_desborde_incluyendo_nul(self):
        a, b = pair("Item", "Señal", "DATABASE.DAT/ARTIFACT.DAT", "6")
        self.assertEqual(check_row(a, b)["estado"], "BLOQUEADO_DESBORDE_CAMPO")

    def test_campo_fijo_permite_ensayo_sin_aprobarlo(self):
        a, b = pair("Item", "Señal", "DATABASE.DAT/ARTIFACT.DAT", "24")
        self.assertEqual(check_row(a, b)["estado"], "CANDIDATO_A_ENSAYO_NO_VALIDADO")

    def test_no_inventa_capacidad(self):
        a, b = pair("Item", "Señal", "DATABASE.DAT/STRTBL.DAT")
        self.assertEqual(check_row(a, b)["estado"], "BLOQUEADO_SIN_MODELO_DE_CAPACIDAD")

    def test_marcador_es_inmutable(self):
        a, b = pair("Hello %s", "Hola %d")
        self.assertEqual(check_row(a, b)["estado"], "BLOQUEADO_MARCADOR")

    def test_byte_de_fuente_corrupto(self):
        a, b = pair()
        b["bytes_hex"] = "00"
        self.assertEqual(check_row(a, b)["estado"], "BLOQUEADO_FUENTE_MODIFICADA")

    def test_grafico_no_es_script(self):
        a, b = pair("NO DATA", "SIN DATOS")
        a["tipo"] = b["tipo"] = "mensaje_grafico"
        self.assertEqual(check_row(a, b)["estado"], "BLOQUEADO_IMAGEN_O_SIN_OFFSET")

    def test_glifo_no_soportado_rechazado(self):
        a, b = pair("Hello?", "🙂")
        self.assertEqual(check_row(a, b)["estado"], "BLOQUEADO_CODIFICACION")

    def test_fuente_incompleta_no_se_corrige_a_ojo(self):
        a, b = pair()
        a["estado"] = b["estado"] = "requiere_reconstruccion"
        self.assertEqual(check_row(a, b)["estado"], "BLOQUEADO_FUENTE_INCOMPLETA")


if __name__ == "__main__":
    unittest.main()
