import re

from ..utils import str_unescape, REGEX_QUOTED
from . import Directive


class WarningDirective(Directive):
    trigger_on = ["warning"]

    def handle(self, line, engine):
        m = re.match(rf'^warning\s+({REGEX_QUOTED})$', line)
        assert m, "malformed"

        engine.log_file_warning(str_unescape(m.group(1)))

class ErrorDirective(Directive):
    trigger_on = ["error"]

    def handle(self, line, engine):
        m = re.match(rf'^error\s+({REGEX_QUOTED})$', line)
        assert m, "malformed"

        msg = str_unescape(m.group(1))
        engine.log_file_error(msg)
        assert False, msg
