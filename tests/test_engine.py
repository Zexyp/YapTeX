import unittest
import os
import tempfile
from difflib import unified_diff

from yaptex.engine import BuildEngine
from yaptex.errors import YapTeXError, BuildError

from . import RESOURCE_DIR

def _cmp_files(expected, actual):
    with open(expected, "r") as f:
        expected_lines = f.readlines()
    with open(actual, "r") as f:
        actual_lines = f.readlines()

    diff = list(unified_diff(expected_lines, actual_lines))
    assert diff == [], "Unexpected file contents:\n" + "".join(diff)

class EngineTest(unittest.TestCase):
    def setUp(self):
        self.engine = BuildEngine()
        self.temp_dir = tempfile.TemporaryDirectory()
        #print("temporary directory: %s" % self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_file(self):
        source = os.path.join(RESOURCE_DIR, "source/file.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source_file=source, output_dir=self.temp_dir.name)

        _cmp_files(source, output)

    def test_include(self):
        source = os.path.join(RESOURCE_DIR, "source/include/include.md")
        ref = os.path.join(RESOURCE_DIR, "expected/include.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        _cmp_files(ref, output)

    def test_line(self):
        source = os.path.join(RESOURCE_DIR, "source/line.md")
        ref = os.path.join(RESOURCE_DIR, "expected/line.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        _cmp_files(ref, output)

    def test_ifs(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/none.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        _cmp_files(ref, output)

    def test_ifs_primary(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/primary.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name, defines=["def_primary"])

        _cmp_files(ref, output)

    def test_ifs_secondary(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/secondary.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name, defines=["def_secondary"])

        _cmp_files(ref, output)

    def test_ifs_both(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/both.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name, defines=["def_primary", "def_secondary"])

        _cmp_files(ref, output)

    def test_heading(self):
        source = os.path.join(RESOURCE_DIR, "source/heading.md")
        ref = os.path.join(RESOURCE_DIR, "expected/heading.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        _cmp_files(ref, output)
    
    def test_variables(self):
        source = os.path.join(RESOURCE_DIR, "source/variables.md")
        ref = os.path.join(RESOURCE_DIR, "expected/variables.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        _cmp_files(ref, output)
    
    def test_macros(self):
        source = os.path.join(RESOURCE_DIR, "source/macros.md")
        ref = os.path.join(RESOURCE_DIR, "expected/macros.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        _cmp_files(ref, output)
    
    def test_include_cyclic(self):
        source = os.path.join(RESOURCE_DIR, "source/include/cyclic.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        try:
            self.engine.build(source, output_dir=self.temp_dir.name)
        except BuildError as ex:
            # we need to check if it's an error for cyclic include
            assert "cyclic" in str(ex)
        else:
            assert False
    
    def test_unended_if(self):
        source = os.path.join(RESOURCE_DIR, "source/bad_if.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.assertRaises(BuildError, lambda: self.engine.build(source, output_dir=self.temp_dir.name))

    def test_multiple_else(self):
        source = os.path.join(RESOURCE_DIR, "source/bad_else.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.assertRaises(BuildError, lambda: self.engine.build(source, output_dir=self.temp_dir.name))
    
    def test_undefined_macro(self):
        source = os.path.join(RESOURCE_DIR, "source/bad_macro.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.assertRaises(BuildError, lambda: self.engine.build(source, output_dir=self.temp_dir.name))
    
    def test_undef(self):
        source = os.path.join(RESOURCE_DIR, "source/undef.md")
        ref = os.path.join(RESOURCE_DIR, "expected/undef.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        _cmp_files(ref, output)
