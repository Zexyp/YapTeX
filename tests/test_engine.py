import unittest
import os
import tempfile
from difflib import unified_diff

from yaptex.engine import BuildEngine
from yaptex.errors import YapTeXError, BuildError

from . import RESOURCE_DIR

def _cmp_files(expected, actual):
    # test the test
    assert os.path.isfile(expected), "wtf"
    assert os.path.isfile(actual), "wtf"
    
    with open(expected, "r") as f:
        expected_lines = f.readlines()
    with open(actual, "r") as f:
        actual_lines = f.readlines()

    diff = list(unified_diff(expected_lines, actual_lines))
    assert diff == [], "Unexpected file contents:\n" + "".join(diff)

class TestEngine(unittest.TestCase):
    def setUp(self):
        self.engine = BuildEngine()
        self.temp_dir = tempfile.TemporaryDirectory()
        #print("temporary directory: %s" % self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _build_test(self, src, ref):
        fullsrc = os.path.join(RESOURCE_DIR, src)
        fullref = os.path.join(RESOURCE_DIR, ref)
        output = os.path.join(self.temp_dir.name, "index.txt")

        self.engine.build(fullsrc, output_dir=self.temp_dir.name)

        _cmp_files(fullref, output)

    def test_file(self):
        source = os.path.join(RESOURCE_DIR, "source/file.md")
        output = os.path.join(self.temp_dir.name, "index.txt")

        self.engine.build(source_file=source, output_dir=self.temp_dir.name)

        _cmp_files(source, output)

    def test_include(self):
        self._build_test(
            "source/include/include.md",
            "expected/include.md")

    def test_line(self):
        self._build_test(
            "source/line.md",
            "expected/line.md")

    def test_ifs(self):
        self._build_test(
            "source/ifs.md",
            "expected/ifs/none.md")

    def test_ifs_primary(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/primary.md")
        output = os.path.join(self.temp_dir.name, "index.txt")

        self.engine.build(source, output_dir=self.temp_dir.name, defines=["def_primary"])

        _cmp_files(ref, output)

    def test_ifs_secondary(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/secondary.md")
        output = os.path.join(self.temp_dir.name, "index.txt")

        self.engine.build(source, output_dir=self.temp_dir.name, defines=["def_secondary"])

        _cmp_files(ref, output)

    def test_ifs_both(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/both.md")
        output = os.path.join(self.temp_dir.name, "index.txt")

        self.engine.build(source, output_dir=self.temp_dir.name, defines=["def_primary", "def_secondary"])

        _cmp_files(ref, output)

    def test_heading(self):
        self._build_test(
            "source/heading.md",
            "expected/heading.md")

    def test_variables(self):
        self._build_test(
            "source/variables.md",
            "expected/variables.md")

    def test_macros(self):
        self._build_test(
            "source/macros.md",
            "expected/macros.md")  
    
    def test_include_cyclic(self):
        source = os.path.join(RESOURCE_DIR, "source/include/cyclic.md")

        try:
            self.engine.build(source, output_dir=self.temp_dir.name)
        except BuildError as ex:
            # we need to check if it's an error for cyclic include
            assert "cyclic" in str(ex)
        else:
            assert False
    
    def test_unended_if(self):
        source = os.path.join(RESOURCE_DIR, "source/bad_if.md")

        self.assertRaises(BuildError, lambda: self.engine.build(source, output_dir=self.temp_dir.name))

    def test_multiple_else(self):
        source = os.path.join(RESOURCE_DIR, "source/bad_else.md")

        self.assertRaises(BuildError, lambda: self.engine.build(source, output_dir=self.temp_dir.name))
    
    def test_undefined_macro(self):
        source = os.path.join(RESOURCE_DIR, "source/bad_macro.md")

        self.assertRaises(BuildError, lambda: self.engine.build(source, output_dir=self.temp_dir.name))
    
    def test_undef(self):
        self._build_test(
            "source/undef.md",
            "expected/undef.md")

    def test_qr(self):
        source = os.path.join(RESOURCE_DIR, "source/qr.md")
        output = os.path.join(self.temp_dir.name, "index.txt")

        self.engine.build(source, output_dir=self.temp_dir.name)

        with open(output, "r") as f:
            txt = f.read().strip()
            assert txt.startswith("<img src=\"data:image/png;base64,") and txt.endswith(">")
    
    def test_frontmatter_simple(self):
        self._build_test(
            "source/frontmatter/basic.md",
            "expected/empty.md")
        assert self.engine.metadata.title == "t"

    def test_pragma_nest(self):
        self._build_test(
            "source/pragma/nest.md",
            "expected/pragma/nest.md")

    def test_pragma_nest_include(self):
        self._build_test(
            "source/pragma/nest_include.md",
            "expected/pragma/nest_include.md")

    def test_pragma_once_include(self):
        self._build_test(
            "source/pragma/once_include.md",
            "expected/pragma/once.md")

