import os
import re
from abc import ABC, abstractmethod
from io import TextIOWrapper, StringIO
from typing import Generator
import sys
from datetime import datetime

from ..utils import *

# #pragma nest

class Directive(ABC):
    trigger_on: list[str] = None

    def __init__(self):
        super().__init__()

        if isinstance(self.trigger_on, str):
            self.trigger_on = [self.trigger_on]

    @abstractmethod
    def handle(self, line: str, engine: 'BuildEngine'):
        pass

class ArgDirective(Directive):
    # arg regex (\s+(.+))?
    pass

from .ifs import *
from .messages import *
from .defines import *

class IncludeDirective(Directive):
    trigger_on = ["include"]

    def handle(self, line, engine):
        m = re.match(rf'^include\s+({REGEX_QUOTED})$', line)
        assert m, "malformed"

        filepath = str_unescape(m.group(1))

        assert engine.current_file

        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        assert os.path.isfile(filepath), f"file '{filepath}' does not exist"
        assert filepath not in engine.filestack, "cyclic include"

        engine.filestack.append(filepath)

        engine.process_file(os.path.join(os.path.dirname(engine.current_file), m.group(1)))

        engine.filestack.pop()


class RegionDirective(Directive):
    trigger_on = ["region"]

    def handle(self, line, engine):
        m = re.match(rf'^region\s+({REGEX_QUOTED})$', line)
        assert m, "malformed"

        section_name = str_unescape(m.group(1))

        engine.sectionstack.append(section_name)

        engine.section_counters.append(1)

        print("hardcoded format")

        engine.feed_raw("#" * len(engine.sectionstack) + f" {section_name}\n")
        # return "#" * len(engine.sectionstack) + f" {'.'.join([str(n) for n in engine.section_counters[0:-1]])}&nbsp;&nbsp;&nbsp;<strong>{section_name}</strong>\n"


class EndRegionDirective(Directive):
    trigger_on = ["endregion"]

    def handle(self, line, engine):
        assert len(engine.sectionstack) > 0, "no section to end"

        engine.section_counters.pop()
        engine.section_counters[-1] += 1

        engine.sectionstack.pop()


class CopyDirective(Directive):
    trigger_on = ["copy"]

    def handle(self, line, engine):
        m = re.match(rf'^copy\s+({REGEX_QUOTED})\s+({REGEX_QUOTED})$', line)
        assert m, "malformed"

        what_file = str_unescape(m.group(1))
        to_dir = str_unescape(m.group(2))

        src_file = os.path.join(os.path.dirname(engine.current_file), what_file)
        assert os.path.isfile(src_file), f"file '{src_file}' does not exist"

        dest_dir = os.path.join(engine.path_dir_output, to_dir)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)

        import shutil

        engine.log_info(f"copying file '{src_file}' to '{dest_dir}'")
        shutil.copy2(src_file, dest_dir)


class PageBreakDirective(Directive):
    trigger_on = ["pagebreak"]

    def handle(self, line, engine):
        # sketchy
        engine.feed_raw('<div style="page-break-before: always;"></div>\n') #<pdf:nextpage/>


class SetDirective(Directive):
    trigger_on = ["set"]

    def handle(self, line, engine):
        m = re.match(rf'^set\s+({REGEX_IDENTIFIER})(?:\s+|\s*=\s*)({REGEX_QUOTED}|{REGEX_NUMBER_INT})',
                     line)  # $ is buggy
        assert m, "malformed"

        variable_name = m.group(1)
        variable_value = str_unescape(m.group(2) or "").strip(QUOTE_CHAR)

        engine.variables[variable_name] = variable_value

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
