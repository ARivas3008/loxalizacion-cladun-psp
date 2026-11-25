"""Synthetic OS fixture tests of PPSSPP v1.20.4 fail-closed preflight (B)."""
import os
import tempfile
import unittest
from pathlib import Path
from tools.f4_r14_ppsspp_preflight import starttime_from_proc_stat, socket_inodes_for_port, attest_local_pid

class TestPreflight(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.proc=self.root/'1234'
        (self.proc/'fd').mkdir(parents=True);(self.root/'net').mkdir()
        (self.proc/'comm').write_text('PPSSPPSDL\n')
        self.iso=self.root/'original.iso';self.iso.write_bytes(b'SYNTHETIC-TEST-ONLY')
        self.app=self.root/'PPSSPP-v1.20.4-anylinux-x86_64.AppImage';self.app.write_bytes(b'SYNTHETIC-APPIMAGE')
        (self.proc/'exe').symlink_to(self.app)
        (self.proc/'environ').write_bytes(('APPIMAGE='+str(self.app)).encode()+b'\x00')
        (self.proc/'cmdline').write_bytes(str(self.app).encode()+b'\x00')
        self.start=456789
        self.write_stat()
        (self.proc/'fd'/'5').symlink_to(self.iso)
        (self.proc/'fd'/'6').symlink_to('socket:[98765]')
        self.write_net('98765')
    def write_stat(self,comm='PPSSPP Test (demo)'):
        fields=['0']*30;fields[18]=str(self.start)
        (self.proc/'stat').write_text('1234 ('+comm+') S '+' '.join(fields)+'\n')
    def write_net(self,inode='98765',port='5E80',state='0A'):
        (self.root/'net'/'tcp').write_text('sl local_address rem_address st tx_queue rx_queue tr tm->when retrnsmt uid timeout inode\n'+
            f'0: 0100007F:{port} 00000000:0000 {state} 00000000:00000000 00:00000000 00000000 1000 0 {inode} 1\n')
    def attest(self):return attest_local_pid(self.root,1234,self.iso,self.app,24192)
    def test_valid_fake_fixture_not_mips(self):
        a=self.attest();self.assertTrue(a['proc_identity_checked']);self.assertFalse(a['ppsspp_MIPS_flow_proven'])
    def test_starttime_with_parentheses(self):
        self.write_stat('PPSSPP (nested) test')
        self.assertEqual(self.attest()['starttime_ticks'],456789)
    def test_wrong_port_fails(self):
        with self.assertRaises(ValueError):attest_local_pid(self.root,1234,self.iso,self.app,24193)
    def test_non_listen_fails(self):
        self.write_net(state='01')
        with self.assertRaises(ValueError):self.attest()
    def test_unauthorized_socket_fails(self):
        self.write_net('76543')
        with self.assertRaises(ValueError):self.attest()
    def test_wrong_iso_inode_fails(self):
        (self.proc/'fd'/'5').unlink()
        with self.assertRaises(ValueError):self.attest()
    def test_wrong_appimage_fails(self):
        (self.proc/'environ').write_bytes(b'APPIMAGE=/wrong/path\x00')
        (self.proc/'cmdline').write_bytes(b'other\x00')
        with self.assertRaises(ValueError):self.attest()
    def test_fake_process_fails(self):
        (self.proc/'comm').write_text('random process\n')
        (self.proc/'exe').unlink();(self.proc/'exe').symlink_to(self.iso)
        with self.assertRaises(ValueError):self.attest()
    def test_invalid_pid_fails(self):
        with self.assertRaises(ValueError):attest_local_pid(self.root,0,self.iso,self.app)
    def test_invalid_port_fails(self):
        with self.assertRaises(ValueError):attest_local_pid(self.root,1234,self.iso,self.app,65536)
    def test_reject_stat_without_starttime(self):
        with self.assertRaises(ValueError):starttime_from_proc_stat('1234 (foo) S 1 2 3')
    def test_socket_inode_extraction(self):
        self.assertEqual(socket_inodes_for_port(self.root,24192),{'98765'})
    def test_missing_proc_fails(self):
        with self.assertRaises(FileNotFoundError):attest_local_pid(self.root,2222,self.iso,self.app)
if __name__=='__main__':unittest.main()
