import unittest
from types import SimpleNamespace as NS
from tools.r45_referencias_locales import scan


def cmd(offset, code, payload, content=None, block=0):
    return NS(offset=offset, code=code, raw=b'\0'*5+payload, content=content, block=block)


class TestScan(unittest.TestCase):
    def test_relative_candidate_and_block_reset(self):
        c = [cmd(100, 0x66, b'', b'a'), cmd(109, 0x22, b'\x09\x00'),
             cmd(200, 0x22, b'\x09\x00', block=1)]
        r = scan(c, [100, 200, 300], {107: 1})
        self.assertEqual(r['moved_commands'], 1)
        self.assertEqual(r['counts']['local_16'], 1)
        self.assertEqual(r['hits'][0]['target_new'], 110)
        self.assertFalse(r['release_authorized'])

    def test_invalid_delta(self):
        with self.assertRaises(ValueError):
            scan([], [0, 10], {7: 1})

    def test_no_movement(self):
        r = scan([cmd(0, 0x22, b'\0'*4)], [0, 10], {})
        self.assertEqual(sum(r['counts'].values()), 0)
        self.assertFalse(r['reference_semantics_proven'])


if __name__ == '__main__':
    unittest.main()
