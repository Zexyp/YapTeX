from abc import ABC, abstractmethod

class Directive(ABC):
    trigger_on: list[str] = None

    def __init__(self):
        super().__init__()

        if isinstance(self.trigger_on, str):
            self.trigger_on = [self.trigger_on]

    @abstractmethod
    def handle(self, line: str, engine: 'BuildEngine'):
        pass

class ArgDirective(Directive, ABC):
    # arg regex (\s+(.+))?
    pass

from .ifs import *
from .messages import *
from .defines import *
from .variables import *
from .files import *
from .regions import *

class PragmaDirective(Directive):
    trigger_on = "pragma"

    def handle(self, line, engine):
        # #pragma nest
        raise NotImplementedError


class PageBreakDirective(Directive):
    trigger_on = ["pagebreak"]

    def handle(self, line, engine):
        # sketchy
        engine.feed_raw('<div style="page-break-before: always;"></div>\n') #<pdf:nextpage/>


class LineDirective(Directive):
    trigger_on = ["line"]

    def handle(self, line, engine):
        pattern = rf'^line\s+({REGEX_NUMBER_INT})(?:\s+{REGEX_GROUP_QUOTED})?$'
        m = re.match(pattern, line)
        if not m: raise MalformedError()

        line_number = m.group(1)
        filename = m.group(2)

        engine.current_file_line_number = int(line_number) - 1
        if filename is not None:
            engine.current_file_alias = filename
