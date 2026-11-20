import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from generar_guion_hablantes import construir, asegurar_fuente, guion


def r(n,kind,txt,order,es='',scene='demo1001_00.dsf'):
    return {'grupo_id':f'{n:06d}', 'text_id':f'CLD-{n:06d}', 'tipo':kind, 'campo':'cadena',
            'origen':'SCRIPT.SDT/SCRIPT.DAT','script':scene,'script_id':'100100',
            'indice_registro':'55', 'orden_script':str(order),'original':txt,'espanol':es,
            'offset_hex':'0x123','bytes_hex':'414243'}

class SpeakerTests(unittest.TestCase):
    def test_speaker_not_leaked_beyond_break(self):
        rows=[r(1,'personaje_interlocutor','Frantic Young Man',191,'Joven frenético'),
              r(2,'dialogo','Do not run!',193,'¡No corras!'),
              r(3,'dialogo','Are you hurt?',194,'¿Estás herido?'),
              r(4,'dialogo','You are muddy',195,'Estás sucio'),
              r(5,'dialogo','I told you not to follow',206,'Te lo dije')]
        indexed,counts=construir(rows)
        self.assertEqual(indexed[1]['hablante_es'],'Joven frenético')
        self.assertEqual(indexed[2]['hablante_es'],'Joven frenético')
        self.assertEqual(indexed[3]['hablante_es'],'Joven frenético')
        self.assertEqual(indexed[4]['hablante_es'],'')
        self.assertIn('[HABLANTE NO VERIFICADO]',guion(indexed))
    def test_new_scene_clears_speaker(self):
        rows=[r(1,'personaje_interlocutor','Hiyoji',7),r(2,'dialogo','Hello',9),
              r(3,'dialogo','Bye',10,scene='other.dsf')]
        indexed,_=construir(rows)
        self.assertEqual(indexed[-1]['hablante_es'],'')
    def test_choice_clears_voice(self):
        rows=[r(1,'personaje_interlocutor','Narrator',7),r(2,'opcion','Yes',9),r(3,'dialogo','OK',10)]
        indexed,_=construir(rows)
        self.assertEqual(indexed[1]['atribucion'],'opcion_del_jugador')
        self.assertFalse(indexed[2]['hablante_es'])
    def test_immutable_guard(self):
        a=r(1,'dialogo','Original',2,'')
        b=a.copy();b['espanol']='Traducción'
        asegurar_fuente([a],[b])
        b['script_id']='999'
        with self.assertRaises(ValueError): asegurar_fuente([a],[b])

if __name__=='__main__':unittest.main()
