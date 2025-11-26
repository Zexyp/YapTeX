"""file operations"""

import os
import re
import shutil

from ..utils import REGEX_GROUP_QUOTED, str_unescape
from . import Directive
from ..errors import BuildError

def _abs_path_warn(file: str, ctx: 'BuildEngine'):
    if os.path.isabs(file):
        ctx.pedantic_log_file("absolute path")
        ctx.assert_that(False)
    else:
        ctx.assert_that(ctx.current_file, "relative include without parent")

class IncludeDirective(Directive):
    """the append thingy"""

    trigger_on = ["include"]

    def handle(self, line, engine):
        m = re.match(rf'^include\s+{REGEX_GROUP_QUOTED}$', line)
        engine.assert_match(m)

        filepath = str_unescape(m.group(1))

        _abs_path_warn(filepath, engine)

        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        engine.assert_file(filepath)
        if not (filepath not in engine.filestack):
            raise BuildError("cyclic include")

        engine.process_file(filepath)

class StyleDirective(Directive):
    """css funny"""

    trigger_on = ["style"]

    def handle(self, line, engine):
        m = re.match(rf'^style\s+{REGEX_GROUP_QUOTED}$', line)
        engine.assert_match(m)

        filepath = str_unescape(m.group(1))

        _abs_path_warn(filepath, engine)

        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        engine.assert_file(filepath)

        raise NotImplementedError

class EmbedDirective(Directive):
    """append but don't process"""

    trigger_on = ["embed"]

    def handle(self, line, engine):
        m = re.match(rf'^embed\s+{REGEX_GROUP_QUOTED}$', line)
        engine.assert_match(m)

        filepath = str_unescape(m.group(1))

        _abs_path_warn(filepath, engine)

        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        engine.assert_file(filepath)

        # TODO: encoding
        # pylint is a fucking yapper
        with open(filepath, "r", encoding=None) as file:
            engine.feed_raw(file.read())


class CopyDirective(Directive):
    """the filesystem bloating mechanism"""

    trigger_on = ["copy"]

    # FIDME: it's unsafe
    def handle(self, line, engine):
        m = re.match(rf'^copy\s+{REGEX_GROUP_QUOTED}\s+{REGEX_GROUP_QUOTED}$', line)
        engine.assert_match(m)

        what_file = str_unescape(m.group(1))
        to_dir = str_unescape(m.group(2))

        _abs_path_warn(what_file, engine)
        _abs_path_warn(to_dir, engine)

        src_file = os.path.join(os.path.dirname(engine.current_file), what_file)
        engine.assert_file(src_file)

        dest_dir = os.path.join(engine.path_dir_output, to_dir)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        engine.log_info(f"copying file '{src_file}' to '{dest_dir}'")
        shutil.copy2(src_file, dest_dir)
