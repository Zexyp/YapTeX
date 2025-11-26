"""more yap generation"""

import re

from ..utils import str_unescape, REGEX_GROUP_QUOTED
from ..errors import BuildError
from . import Directive


class WarningDirective(Directive):
    """yap"""

    trigger_on = ["warning"]

    def handle(self, line, engine):
        m = re.match(rf'^warning\s+{REGEX_GROUP_QUOTED}$', line)
        engine.assert_match(m)

        msg = str_unescape(m.group(1))
        engine.log_file_warning(f"warning: {msg}")

class ErrorDirective(Directive):
    """yap n fail"""

    trigger_on = ["error"]

    def handle(self, line, engine):
        m = re.match(rf'^error\s+{REGEX_GROUP_QUOTED}$', line)
        engine.assert_match(m)

        msg = str_unescape(m.group(1))
        engine.log_file_error(f"error: {msg}")
        raise BuildError(msg)
