import unittest
import os
import tempfile

from yaptex.engine import BuildEngine
from yaptex.errors import YapTeXError

from . import RESOURCE_DIR

class EngineTest(unittest.TestCase):
    def setUp(self):
        self.engine = BuildEngine()
        self.temp_dir = tempfile.TemporaryDirectory()
        #print("temporary directory: %s" % self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _cmp_files(self, expected, actual):
        from difflib import unified_diff

        with open(expected, "r") as f:
            expected_lines = f.readlines()
        with open(actual, "r") as f:
            actual_lines = f.readlines()

        diff = list(unified_diff(expected_lines, actual_lines))
        assert diff == [], "Unexpected file contents:\n" + "".join(diff)

    def test_file(self):
        source = os.path.join(RESOURCE_DIR, "hello.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source_file=source, output_dir=self.temp_dir.name)

        self._cmp_files(source, output)

    def test_include_cyclic(self):
        source = os.path.join(RESOURCE_DIR, "source/include/cyclic_include.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.assertRaises(YapTeXError, lambda: self.engine.build(source, output_dir=self.temp_dir.name))

    def test_include(self):
        source = os.path.join(RESOURCE_DIR, "source/include/include.md")
        ref = os.path.join(RESOURCE_DIR, "expected/include.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        self._cmp_files(ref, output)

    def test_line(self):
        source = os.path.join(RESOURCE_DIR, "source/line.md")
        ref = os.path.join(RESOURCE_DIR, "expected/line.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        self._cmp_files(ref, output)

    def test_ifs(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/none.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        self._cmp_files(ref, output)

    def test_ifs_primary(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/primary.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name, defines=["def_primary"])

        self._cmp_files(ref, output)

    def test_ifs_secondary(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/secondary.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name, defines=["def_secondary"])

        self._cmp_files(ref, output)

    def test_ifs_both(self):
        source = os.path.join(RESOURCE_DIR, "source/ifs.md")
        ref = os.path.join(RESOURCE_DIR, "expected/ifs/both.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name, defines=["def_primary", "def_secondary"])

        self._cmp_files(ref, output)

    def test_heading(self):
        source = os.path.join(RESOURCE_DIR, "source/heading.md")
        ref = os.path.join(RESOURCE_DIR, "expected/heading.md")
        output = os.path.join(self.temp_dir.name, "index.md")

        self.engine.build(source, output_dir=self.temp_dir.name)

        self._cmp_files(ref, output)