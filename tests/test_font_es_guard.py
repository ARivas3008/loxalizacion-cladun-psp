#!/usr/bin/env python3
"""Optional destructive-negative tests, isolated in a temporary copy.

Run with CLADUN_SOURCE_ISO=/private/orig.iso and
CLADUN_TEST_CANDIDATE_ISO=/private/test.iso. Without them tests are skipped.
Never commit candidate or source ISOs.
"""
import os,unittest,tempfile,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'tools'))
from font_es_guard import verify,inspect

SOURCE=os.environ.get('CLADUN_SOURCE_ISO')
CANDIDATE=os.environ.get('CLADUN_TEST_CANDIDATE_ISO')

@unittest.skipUnless(SOURCE and CANDIDATE,'Private source/candidate ISO not configured')
class TestFontIsolation(unittest.TestCase):
    def test_positive_and_four_negative_changes(self):
        source,candidate=Path(SOURCE),Path(CANDIDATE)
        verify(source,candidate)
        _,data,pack,items=inspect(source)
        font=next(x for x in items if x['name']=='FONT.ARC')
        other=next(x for x in items if x['name'] not in ('FONT.ARC','DATA.DAT') and x['size_stored']>100)
        positions=[
            data['offset']+other['offset']+100,
            data['offset']+16,
            data['offset']+font['offset']+620,
            data['offset']+font['offset']+font['size_stored']+460
        ]
        with tempfile.TemporaryDirectory() as tmp:
            bad=Path(tmp)/'private_bad.iso'
            for position in positions:
                shutil.copyfile(candidate,bad)
                with bad.open('r+b') as f:
                    f.seek(position);old=f.read(1);f.seek(position);f.write(bytes([old[0]^1]))
                with self.assertRaises((ValueError,AssertionError)):
                    verify(source,bad)

if __name__=='__main__':unittest.main()
