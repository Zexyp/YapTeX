import re, os

from . import Directive
from .files import _abs_path_warn as _abs_pth_wrn
from ..utils import REGEX_GROUP_QUOTED, str_unescape

class StyleDirective(Directive):
    """the append style thingy"""

    trigger_on = ["style"]

    def handle(self, line, engine):
        m = re.match(rf'^style\s+{REGEX_GROUP_QUOTED}$', line)
        engine.assert_match(m)

        filepath = str_unescape(m.group(1))

        _abs_pth_wrn(filepath, engine)

        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        engine.assert_file(filepath)
        engine.metadata.stylelist.append(filepath)
