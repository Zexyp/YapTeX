from ..utils import *
from . import Directive

# does not go into negatives
def _modify_last(text, increment):
    mchs = list(re.finditer(REGEX_NUMBER_INT, text))
    if not mchs:
        return (text + str(increment)) if increment > 0 else text

    last = mchs[-1]
    start, end = last.span()
    old = text[start:end]
    value = int(old) + increment
    return text[:start] + (str(value) if value > 0 else "") + text[end:]

class SetDirective(Directive):
    trigger_on = ["set"]

    def handle(self, line, engine):
        m = re.match(rf'^set\s+({REGEX_IDENTIFIER})(?:\s+|\s*=\s*)({REGEX_QUOTED}|{REGEX_NUMBER_INT})',
                     line)  # $ is buggy
        assert m, "malformed"

        variable_name = m.group(1)
        variable_value = str_unescape((m.group(2) or "").strip(QUOTE_CHAR))

        engine.variables[variable_name] = variable_value

class IncrementDirective(Directive):
    trigger_on = ["inc"]

    def handle(self, line, engine):
        m = re.match(rf'^inc\s+({REGEX_IDENTIFIER})(?:\s+({REGEX_NUMBER_INT}))?$', line)
        assert m, "malformed"

        variable_name = m.group(1)
        by = m.group(2)

        assert variable_name in engine.variables, f"undefined variable '{variable_name}'"
        
        increment = int(by) if by else 1
        last_value = engine.variables[variable_name]
        new_value = str(int(last_value) + increment) if re.match(REGEX_NUMBER_INT, last_value) else _modify_last(last_value, increment)

        engine.variables[variable_name] = new_value


class DecrementDirective(Directive):
    trigger_on = ["dec"]

    def handle(self, line, engine):
        m = re.match(rf'^dec\s+({REGEX_IDENTIFIER})(?:\s+({REGEX_NUMBER_INT}))?$', line)
        assert m, "malformed"

        variable_name = m.group(1)
        by = m.group(2)

        assert variable_name in engine.variables, f"undefined variable '{variable_name}'"

        increment = -(int(by) if by else 1)
        last_value = engine.variables[variable_name]
        new_value = str(int(last_value) + increment) if re.match(REGEX_NUMBER_INT, last_value) else _modify_last(last_value, increment)

        engine.variables[variable_name] = new_value