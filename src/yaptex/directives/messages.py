import re

from ..utils import str_unescape, REGEX_GROUP_QUOTED
from ..errors import *
from . import Directive


class WarningDirective(Directive):
    trigger_on = ["warning"]

    def handle(self, line, engine):
        m = re.match(rf'^warning\s+{REGEX_GROUP_QUOTED}$', line)
        if not m: raise MalformedError()

        msg = str_unescape(m.group(1))
        engine.log_file_warning(msg)

class ErrorDirective(Directive):
    trigger_on = ["error"]

    def handle(self, line, engine):
        m = re.match(rf'^error\s+{REGEX_GROUP_QUOTED}$', line)
        if not m: raise MalformedError()

        msg = str_unescape(m.group(1))
        engine.log_file_error(msg)
        raise BuildError(msg)
