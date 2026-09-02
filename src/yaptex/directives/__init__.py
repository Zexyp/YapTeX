"""base directives"""

from abc import ABC, abstractmethod
import re
import argparse
import shlex

from ..utils import REGEX_NUMBER_INT, REGEX_GROUP_QUOTED

# TODO: decide if feed raw or with variables emplaced

class Directive(ABC):
    """mechanism to declare logic of directives"""

    trigger_on: list[str] = None

    def __init__(self):
        super().__init__()

        if isinstance(self.trigger_on, str):
            self.trigger_on = [self.trigger_on]

    @abstractmethod
    def handle(self, line: str, engine: 'BuildEngine'):
        """logic goes here"""

class ArgDirective(Directive, ABC):
    """handle directive using argparse"""

    # arg regex (\s+(.+))?
    def __init__(self):
        super().__init__()

        self.parser = self.build_parser()
    
    def handle(self, line: str, engine: 'BuildEngine'):
        line = line.split(" ", maxsplit=1)[-1]
        line = engine.handle_variables(line, engine.variables)
        line_args = shlex.split(line)
        
        try:
            try:
                args = self.parser.parse_args(line_args)
            except SystemExit as e:
                engine.assert_that(False, "arg directive failed")
            
            if not hasattr(args, "func"):
                raise argparse.ArgumentError(message="unusable")
            
            engine.feed_raw(args.func(args))
        except argparse.ArgumentError as e:
            msg = msg.strip()
            engine.assert_that(False, msg)
    
    @abstractmethod
    def build_parser(self) -> argparse.ArgumentParser:
        """parser build goes here"""

from .ifs import IfDirective,  IfDefDirective
from .messages import WarningDirective, ErrorDirective
from .defines import DefineDirective, UndefineDirective
from .variables import SetDirective, IncrementDirective, DecrementDirective
from .files import IncludeDirective, EmbedDirective, CopyDirective, StyleDirective
from .regions import RegionDirective, EndRegionDirective
from .qr import QrDirective

class PragmaDirective(Directive):
    """today is not the day"""

    trigger_on = "pragma"

    def handle(self, line, engine):
        # #pragma nest
        raise NotImplementedError


class PageBreakDirective(Directive):
    """inserts page breaking feature"""

    trigger_on = ["pagebreak"]

    def handle(self, line, engine):
        # sketchy
        engine.feed_raw('<div style="page-break-before: always;"></div>\n') #<pdf:nextpage/>


class LineDirective(Directive):
    """the rename spaghetification device"""

    trigger_on = ["line"]

    def handle(self, line, engine):
        pattern = rf'^line\s+({REGEX_NUMBER_INT})(?:\s+{REGEX_GROUP_QUOTED})?$'
        m = re.match(pattern, line)
        engine.assert_match(m)

        line_number = m.group(1)
        filename = m.group(2)

        engine.current_file_line_number = int(line_number) - 1
        if filename is not None:
            engine.current_file_alias = filename
