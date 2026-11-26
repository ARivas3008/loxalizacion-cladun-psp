import unittest
from tools.r60_layout_guard import classify_padding, check_bestiary, group_advance_result

class TestR60LayoutGuard(unittest.TestCase):
    def test_padding_is_not_removed(self):
        raw=b'Una palabra   '
        self.assertEqual(classify_padding(raw),dict(leading=0,trailing=3,consecutive=True,internal_consecutive=False))
        self.assertEqual(raw,b'Una palabra   ')
        self.assertTrue(classify_padding(b'Una  palabra')['internal_consecutive'])
    def test_cell_width_and_height(self):
        self.assertEqual(check_bestiary(b'A'*18,'nombre'),'overflow')
        self.assertEqual(check_bestiary(b'A'*17,'nombre'),'pass_provisional_cell_bound')
        self.assertEqual(check_bestiary(b'A'*36,'descripcion'),'overflow')
        self.assertEqual(check_bestiary(b'A'*35,'descripcion'),'pass_provisional_cell_bound')
        self.assertEqual(check_bestiary(b'A\n'*5+b'A','descripcion'),'overflow')
    def test_unknown_not_passed(self):
        self.assertEqual(check_bestiary(b'A','stat'),'geometry_pending')
        self.assertEqual(check_bestiary(b'\xb4','descripcion'),'encoding_pending')
        self.assertEqual(check_bestiary(b'\x81\x40','descripcion'),'encoding_pending')
    def test_real_group_regression(self):
        self.assertEqual(group_advance_result(668,605),'FAIL_RENDER_ADVANCE')
        self.assertEqual(group_advance_result(668,667),'PASS')
if __name__=='__main__':unittest.main()
