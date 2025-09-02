import os
import re
from abc import ABC, abstractmethod
from io import TextIOWrapper, StringIO
from typing import Generator
import sys
from datetime import datetime

from ..utils import *

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
from .variables import *
from .files import *

class PragmaDirective(Directive):
    trigger_on = "pragma"

    def handle(self, line, engine):
        # #pragma nest
        raise NotImplementedError


class RegionDirective(Directive):
    trigger_on = ["region"]

    def handle(self, line, engine):
        m = re.match(rf'^region\s+({REGEX_QUOTED})$', line)
        assert m, "malformed"

        section_name = str_unescape(m.group(1).strip(QUOTE_CHAR))

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


class PageBreakDirective(Directive):
    trigger_on = ["pagebreak"]

    def handle(self, line, engine):
        # sketchy
        engine.feed_raw('<div style="page-break-before: always;"></div>\n') #<pdf:nextpage/>


class LineDirective(Directive):
    trigger_on = ["line"]

    def handle(self, line, engine):
        pattern = rf'^line\s+({REGEX_NUMBER_INT})(?:\s+({REGEX_QUOTED}))?$'
        m = re.match(pattern, line)
        assert m, "malformed"

        line_number = m.group(1)
        filename = m.group(2)
        
        engine.current_file_line_number = int(line_number) - 1
        if filename is not None:
            engine.current_file_alias = filename
