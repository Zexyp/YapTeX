import re

from . import Directive
from ..engine import Macro
from ..utils import *


class DefineDirective(Directive):
    trigger_on = "define"

    # todo: add elipsis, multiline fuckery (escaping)
    def handle(self, line, engine):
        pattern = rf'^define\s+({REGEX_IDENTIFIER})(\(\s*{REGEX_IDENTIFIER}\s*({MACRO_ARG_SEPARATOR}\s*{REGEX_IDENTIFIER}\s*)*\))?(\s+(.*?)({REGEX_MACRO_LINE_CONTINUE})?)?$'
        m = re.match(pattern, line)
        assert m, "malformed"

        macro_name = m.group(1)
        macro_params = m.group(2)

        body_line = m.group(5)
        continue_next_line = m.group(6) is not None

        assert macro_name not in engine.macros, "macro redefinition"

        m = Macro()
        m.params = None
        m.body = body_line

        if macro_params:
            m.params = [x.strip() for x in macro_params.strip("()").split(MACRO_ARG_SEPARATOR)]

        if continue_next_line:
            for body_line in engine.consume():
                body_line = body_line.strip()
                if continue_next_line := body_line.endswith(MACRO_LINE_CONTINUE):
                    body_line = body_line.removesuffix(MACRO_LINE_CONTINUE)
                m.body += f"\n{body_line}"

                # escape the pain
                if not continue_next_line:
                    break
            else:
                assert False, "unended macro"

        engine.macros[macro_name] = m


class UndefineDirective(Directive):
    trigger_on = "undef"

    def handle(self, line, engine):
        m = re.match(rf'^undef\s+{REGEX_GROUP_IDENTIFIER}$', line)
