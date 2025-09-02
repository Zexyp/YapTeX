import re

from . import Directive
from ..structures import Macro
from ..utils import *

class DefineDirective(Directive):
    trigger_on = ["define"]

    # todo: add elipsis, multiline fuckery (escaping)
    def handle(self, line, engine):
        pattern = rf'^define\s+({REGEX_IDENTIFIER})(\(\s*{REGEX_IDENTIFIER}\s*(?:{REGEX_MACRO_ARG_SEPARATOR}\s*{REGEX_IDENTIFIER}\s*)*\))?(?:\s+(.*?)({REGEX_MACRO_LINE_CONTINUE})?)?$'
        m = re.match(pattern, line)
        assert m, "malformed"

        macro_name = m.group(1)
        macro_params = m.group(2)

        body_line = m.group(3)
        continue_next_line = m.group(4) is not None

        assert macro_name not in engine.macros, "redefinition"

        mac = Macro()
        mac.params = None
        mac.body = body_line
        mac.file = engine.currnet_file

        if macro_params:
            mac.params = [x.strip() for x in macro_params.strip("()").split(MACRO_ARG_SEPARATOR)]

        def eat_macro():
            for body_line in engine.consume():
                # allow leading spaces
                # TODO: handle better
                if body_line.startswith(ESCAPE_CHAR):
                    body_line = body_line.removeprefix(ESCAPE_CHAR).rstrip()
                else:
                    body_line = body_line.strip()

                # consume line continuation
                if continue_next_line := body_line.endswith(MACRO_LINE_CONTINUE):
                    body_line = body_line.removesuffix(MACRO_LINE_CONTINUE)

                mac.body += f"\n{body_line}"

                # escape the pain
                if not continue_next_line:
                    break
            else:
                assert False, "unended macro"

        if continue_next_line:
            eat_macro()

        engine.macros[macro_name] = mac


class UndefineDirective(Directive):
    trigger_on = ["undef"]

    def handle(self, line, engine):
        m = re.match(rf'^undef\s+({REGEX_IDENTIFIER})$', line)

        assert m, "malformed"

        macro_name = m.group(1)

        assert macro_name in engine.macros, f"'{macro_name}' is not defined"

        del engine.macros[macro_name]
