import os

from ..utils import *
from ..errors import *
from . import Directive

def _abs_path_warn(file: str, ctx: 'BuildEngine'):
    if os.path.isabs(file):
        ctx.pedantic_log_file("absolute path")
        ctx.assert_that(False)
    else:
        assert ctx.current_file, "relative include without parent"

class IncludeDirective(Directive):
    trigger_on = ["include"]

    def handle(self, line, engine):
        m = re.match(rf'^include\s+{REGEX_GROUP_QUOTED}$', line)
        if not m: raise MalformedError()

        filepath = str_unescape(m.group(1))

        _abs_path_warn(filepath, engine)

        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        engine.assert_file(filepath)
        assert filepath not in engine.filestack, "cyclic include"

        engine.process_file(filepath)

class StyleDirective(Directive):
    trigger_on = ["style"]

    def handle(self, line, engine):
        m = re.match(rf'^style\s+{REGEX_GROUP_QUOTED}$', line)
        if not m: raise MalformedError()

        filepath = str_unescape(m.group(1))

        _abs_path_warn(filepath, engine)

        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        engine.assert_file(filepath)

        raise NotImplementedError

class EmbedDirective():
    trigger_on = ["embed"]

    def handle(self, line, engine):
        m = re.match(rf'^embed\s+{REGEX_GROUP_QUOTED}$', line)
        if not m: raise MalformedError()

        filepath = str_unescape(m.group(1))

        _abs_path_warn(filepath, engine)

        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        engine.assert_file(filepath)

        with open(filepath, "r") as file:
            engine.feed_raw(file.read())


class CopyDirective(Directive):
    trigger_on = ["copy"]

    def handle(self, line, engine):
        m = re.match(rf'^copy\s+{REGEX_GROUP_QUOTED}\s+{REGEX_GROUP_QUOTED}$', line)
        if not m: raise MalformedError()

        what_file = str_unescape(m.group(1))
        to_dir = str_unescape(m.group(2))

        _abs_path_warn(what_file, engine)
        _abs_path_warn(to_dir, engine)

        src_file = os.path.join(os.path.dirname(engine.current_file), what_file)
        engine.assert_file(src_file)

        dest_dir = os.path.join(engine.path_dir_output, to_dir)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        import shutil

        engine.log_info(f"copying file '{src_file}' to '{dest_dir}'")
        shutil.copy2(src_file, dest_dir)
