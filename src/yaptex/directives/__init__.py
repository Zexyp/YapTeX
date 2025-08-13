import os
import re
from abc import ABC, abstractmethod
from io import TextIOWrapper, StringIO
from typing import Generator
import sys
from datetime import datetime

from ..engine import Macro
from ..utils import *


class Directive(ABC):
    # arg regex (\s+(.+))?
    trigger_on: str = None

    @abstractmethod
    def handle(self, line: str, engine: 'BuildEngine'):
        pass

from .ifs import *
from .messages import *
from .defines import *

class IncludeDirective(Directive):
    trigger_on = "include"

    def handle(self, line, engine):
        m = re.match(rf'^include\s+{REGEX_GROUP_QUOTED}$', line)
        assert m, "malformed"

        filepath = str_unescape(m.group(1))

        assert engine.current_file

        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        assert os.path.isfile(filepath), f"file '{filepath}' does not exist"
        assert filepath not in engine.filestack, "cyclic include"

        engine.filestack.append(filepath)

        engine.process_file(os.path.join(os.path.dirname(engine.current_file), m.group(1)))

        engine.filestack.pop()


class SectionDirective(Directive):
    trigger_on = "section"

    def handle(self, line, engine):
        m = re.match(rf'^section\s+{REGEX_GROUP_QUOTED}$', line)
        assert m, "malformed"

        section_name = str_unescape(m.group(1))

        engine.sectionstack.append(section_name)

        engine.section_counters.append(1)

        print("hardcoded format")

        engine.feed_raw("#" * len(engine.sectionstack) + f" {section_name}\n")
        # return "#" * len(engine.sectionstack) + f" {'.'.join([str(n) for n in engine.section_counters[0:-1]])}&nbsp;&nbsp;&nbsp;<strong>{section_name}</strong>\n"


class EndSectionDirective(Directive):
    trigger_on = "endsect"

    def handle(self, line, engine):
        assert len(engine.sectionstack) > 0, "no section to end"

        engine.section_counters.pop()
        engine.section_counters[-1] += 1

        engine.sectionstack.pop()


class CopyDirective(Directive):
    trigger_on = "copy"

    def handle(self, line, engine):
        m = re.match(rf'^copy\s+{REGEX_GROUP_QUOTED}\s+{REGEX_GROUP_QUOTED}$', line)
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
    trigger_on = "pagebreak"

    def handle(self, line, engine):
        # sketchy
        engine.feed_raw('<div style="page-break-before: always;"></div>\n') #<pdf:nextpage/>


class SetDirective(Directive):
    trigger_on = "set"

    def handle(self, line, engine):
        m = re.match(rf'^set\s+({REGEX_IDENTIFIER})\s*=\s*(?:{REGEX_GROUP_QUOTED}|({REGEX_NUMBER}))',
                     line)  # $ is buggy
        assert m, "malformed"

        variable_name = m.group(1)
        variable_value = str_unescape(m.group(2) or m.group(3) or "")

        engine.variables[variable_name] = variable_value


class IncrementDirective(Directive):
    trigger_on = "inc"

    def handle(self, line, engine):
        m = re.match(rf'^inc\s+({REGEX_IDENTIFIER})\s+({REGEX_NUMBER})$', line)
        assert m, "malformed"

        variable_name = m.group(1)
        by = m.group(2)

        assert variable_name in engine.variables, f"undefined variable '{variable_name}'"

        # todo: fix
        value = int(engine.variables[variable_name])
        increment = int(by)

        engine.variables[variable_name] = str(value + increment)


class DecrementDirective(Directive):
    trigger_on = "dec"

    def handle(self, line, engine):
        m = re.match(rf'^dec\s+({REGEX_IDENTIFIER})\s+({REGEX_NUMBER})$', line)
        assert m, "malformed"

        variable_name = m.group(1)
        by = m.group(2)

        assert variable_name in engine.variables, f"undefined variable '{variable_name}'"

        # todo: fix
        value = int(engine.variables[variable_name])
        decrement = int(by)

        engine.variables[variable_name] = str(value - decrement)
