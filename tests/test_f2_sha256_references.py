"""Prevent 62-character Cladun USA ISO SHA-256 from appearing in releases/docs."""
import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
USA_SHA="b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f"
WRONG_62=USA_SHA[:24]+USA_SHA[26:]
TEXT_EXTS={'.py','.md','.json','.txt','.go','.yml','.yaml','.sh','.toml'}
SCANNED_DIRS=("docs","reports","prompts","tools","tests","patcher",".github")

class SourceSHA256Guard(unittest.TestCase):
    def test_sha_reference_is_exact_64_characters(self):
        self.assertEqual(len(USA_SHA),64)
        self.assertEqual(len(WRONG_62),62)
        self.assertNotEqual(USA_SHA,WRONG_62)

    def test_protected_scripts_use_real_64_character_sha(self):
        sources=[("tools/f2_auditar_origen_iconos.py","ISO_SHA256"),
                 ("tools/f2_ram_provenance_1204.py","USA_SHA"),
                 ("tools/font_es_patch.py","SOURCE_SHA256")]
        for file,name in sources:
            with self.subTest(file=file,name=name):
                tree=ast.parse((ROOT/file).read_text(encoding="utf-8"))
                values=[statement.value.value for statement in tree.body
                        if isinstance(statement,(ast.Assign,ast.AnnAssign))
                        for target in (statement.targets if isinstance(statement,ast.Assign) else [statement.target])
                        if isinstance(target,ast.Name) and target.id==name
                        and isinstance(statement.value,ast.Constant)
                        and isinstance(statement.value.value,str)]
                self.assertEqual(values,[USA_SHA])

    def test_no_truncated_source_sha_in_repository_text(self):
        errors=[]
        for d in SCANNED_DIRS:
            folder=ROOT/d
            if not folder.exists():
                continue
            for p in folder.rglob('*'):
                if p.is_file() and p.suffix.lower() in TEXT_EXTS and WRONG_62 in p.read_text(encoding="utf-8"):
                    errors.append(str(p.relative_to(ROOT)))
        for name in ("AGENTS.md","README.md"):
            p=ROOT/name
            if p.exists() and WRONG_62 in p.read_text(encoding="utf-8"):
                errors.append(name)
        self.assertEqual(errors,[],"SHA USA truncado en: "+", ".join(errors))

if __name__=='__main__':
    unittest.main()
