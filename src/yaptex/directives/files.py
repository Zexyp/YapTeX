import os

from ..utils import *
from . import Directive

class IncludeDirective(Directive):
    trigger_on = ["include"]

    def handle(self, line, engine):
        m = re.match(rf'^include\s+({REGEX_QUOTED})$', line)
        assert m, "malformed"

        filepath = str_unescape(m.group(1).strip(QUOTE_CHAR))

        if os.path.isabs(filepath):
            engine.pedantic_log_file("absolute path")
            assert False
        else:
            assert engine.current_file, "relative include without parent"

        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        assert os.path.isfile(filepath), f"file '{filepath}' does not exist"
        assert filepath not in engine.filestack, "cyclic include"

        engine.process_file(filepath)

class EmbedDirective():
    trigger_on = ["embed"]

    def handle(self, line, engine):
        m = re.match(rf'^embed\s+({REGEX_QUOTED})$', line)
        assert m, "malformed"

        filepath = str_unescape(m.group(1).strip(QUOTE_CHAR))

        if os.path.isabs(filepath):
            engine.pedantic_log_file("absolute path")
            assert False
        else:
            assert engine.current_file, "relative include without parent"
        
        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        assert os.path.isfile(filepath), f"file '{filepath}' does not exist"
        
        with open(filepath, "r") as file:
            engine.feed_raw(file.read())


class CopyDirective(Directive):
    trigger_on = ["copy"]

    def handle(self, line, engine):
        m = re.match(rf'^copy\s+({REGEX_QUOTED})\s+({REGEX_QUOTED})$', line)
        assert m, "malformed"

        what_file = str_unescape(m.group(1).strip(QUOTE_CHAR))
        to_dir = str_unescape(m.group(2).strip(QUOTE_CHAR))

        src_file = os.path.join(os.path.dirname(engine.current_file), what_file)
        assert os.path.isfile(src_file), f"file '{src_file}' does not exist"

        dest_dir = os.path.join(engine.path_dir_output, to_dir)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        import shutil

        engine.log_info(f"copying file '{src_file}' to '{dest_dir}'")
        shutil.copy2(src_file, dest_dir)