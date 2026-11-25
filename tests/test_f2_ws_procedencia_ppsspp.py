"""Synthetic-only regression for socket inode ownership: no game files."""
import sys
import unittest
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from f2_ws_procedencia_ppsspp import parse_listeners, listener_inodes, owned_socket_inodes, ownership, SHA_ISO, ISO_BYTES

HEADER = 'sl local_address rem_address st tx_queue rx_queue tr tm->when retrnsmt uid timeout inode'
IPV6 = '0: 00000000000000000000000000000000:5E80 0000:0000 0A 0:0 0:0 00:0 00000000 0 12758'
IPV4 = '0: 0100007F:5E80 00000000:0000 0A 0:0 0:0 00:0 00000000 0 12758'

class SocketOwnershipTests(unittest.TestCase):
    def test_listen_port(self):
        self.assertEqual(parse_listeners(HEADER + '\n' + IPV6, 24192), {12758})
    def test_different_port(self):
        self.assertEqual(parse_listeners(HEADER + '\n' + IPV6, 24193), set())
    def test_established_ignored(self):
        self.assertEqual(parse_listeners(HEADER + '\n' + IPV4.replace(' 0A ', ' 01 '), 24192), set())
    def test_zero_inode_ignored(self):
        self.assertEqual(parse_listeners(HEADER + '\n' + IPV4.replace('12758', '0'), 24192), set())
    def test_malformed_ignored(self):
        self.assertEqual(parse_listeners(HEADER + '\ninvalid line\n', 24192), set())
    def test_invalid_ports(self):
        for value in (-1, 0, 65536, False, '24192'):
            with self.assertRaises(ValueError):
                parse_listeners(HEADER, value)
    def test_proc_fd_and_listener_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'net').mkdir()
            (root / '123/fd').mkdir(parents=True)
            (root / 'net/tcp').write_text(HEADER + '\n')
            (root / 'net/tcp6').write_text(HEADER + '\n' + IPV6 + '\n')
            (root / '123/fd/4').symlink_to('socket:[12758]')
            (root / '123/fd/5').symlink_to('socket:[50000]')
            self.assertEqual(listener_inodes(24192, root), {12758})
            self.assertEqual(owned_socket_inodes(123, root), {12758, 50000})
            self.assertEqual(ownership(123, 24192, root), {12758})
    def test_other_pid_not_matched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'net').mkdir()
            (root / '999/fd').mkdir(parents=True)
            (root / 'net/tcp').write_text(HEADER + '\n')
            (root / 'net/tcp6').write_text(HEADER + '\n' + IPV6 + '\n')
            (root / '999/fd/3').symlink_to('socket:[99999]')
            self.assertEqual(ownership(999, 24192, root), set())
    def test_pinned_f1_sha_and_size(self):
        self.assertEqual(SHA_ISO['f1'], '496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986')
        self.assertEqual(ISO_BYTES['f1'], 306456576)

if __name__ == '__main__':
    unittest.main()
