import unittest
from tools.r61_executable_patch import patch_elf,PATCHES,SIZE
class TestR61(unittest.TestCase):
    def test_bad_dump(self):
        with self.assertRaises(ValueError): patch_elf(b'\x7fELF'+bytes(SIZE-4))
    def test_ranges(self):
        self.assertEqual([len(x[1]) for x in PATCHES],[8,68,72])
        for off,data in PATCHES: self.assertLessEqual(off+len(data),SIZE)
    def test_classifier_model(self):
        for c in range(256):
            lead=((c-0x81)&0xffffffff)<31 or ((c-0xe0)&0xffffffff)<29
            self.assertEqual(lead,0x81<=c<0xa0 or 0xe0<=c<0xfd)
            flag=0 if lead else 1^int(((c-0xb4)&0xffffffff)<44)
            self.assertEqual(flag,int(not lead and not 0xb4<=c<=0xdf))
