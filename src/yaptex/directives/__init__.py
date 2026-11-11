"""base directives"""

from abc import ABC, abstractmethod
import re
import argparse
import shlex

from ..utils import REGEX_NUMBER_INT, REGEX_GROUP_QUOTED
from ..log import log_error

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine import BuildEngine

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
                args: ArgDirective.BaseArgs = self.parser.parse_args(line_args)
                args.engine = engine
            except SystemExit as e:
                engine.assert_that(False, "arg directive failed")
            
            if not hasattr(args, "func"):
                raise argparse.ArgumentError(message="unusable")

            l = args.func(args)
            if l is not None:
                engine.feed_raw(l)
        except argparse.ArgumentError as e:
            msg = msg.strip()
            engine.assert_that(False, msg)
    
    @abstractmethod
    def build_parser(self) -> argparse.ArgumentParser:
        """parser build goes here"""

    class BaseArgs:
        engine: 'BuildEngine' = None

from .ifs import IfDirective,  IfDefDirective
from .messages import WarningDirective, ErrorDirective
from .defines import DefineDirective, UndefineDirective
from .variables import SetDirective, IncrementDirective, DecrementDirective
from .files import IncludeDirective, EmbedDirective, CopyDirective, StyleDirective
from .regions import RegionDirective, EndRegionDirective


try:
    from .qr import QrDirective
except ImportError as e:
    log_error(f"failed to import directive: {e}")
    QrDirective = None

class PragmaDirective(ArgDirective):
    """today is not the day"""

    trigger_on = ["pragma"]

    def _parse_bracketed_args(self, items, actions: list[str], slots: list[str], kwonly: list[str] = []) -> tuple[list[str], dict[str, str]]:
        bare = []
        out_actions = []
        out_opts = {}

        for item in items:
            assert item
            if "=" in item:
                key, value = (part.strip() for part in item.split("=", 1))
                assert key in slots or key in kwonly, f"unknown key '{key}'"
                assert key not in out_opts, f"duplicate value for '{key}'"
                out_opts[key] = value
            elif item in actions:
                out_actions.append(item)
            else:
                bare.append(item)

        free = [slot for slot in slots if slot not in out_opts]
        assert len(bare) <= len(free), "too many positional values"

        for slot, value in zip(free, bare):
            out_opts[slot] = value

        for opt in (*slots, *kwonly):
            out_opts.setdefault(opt, None)
        return out_actions, out_opts

    def _func_hlevel(self, args: ArgDirective.BaseArgs):
        # TODO: hlevel arabic, roman, greek, alphabetical
        # TODO: custom format
        pattern = rf'^count\s*\((.*)\)'
        rest = " ".join(args.rest)
        m = re.match(pattern, rest)
        args.engine.assert_match(m)

        actions, opts = self._parse_bracketed_args([i.strip() for i in m.group(1).split(",")],
                                                    ["push", "pop", "reset"],
                                                    ["start", "end"],
                                                    ["depth"])

        assert len(actions) <= 1
        act = actions[0] if actions else None

        if not act and not opts:
            raise NotImplementedError("#pragma hlevel count() defaults")

        if act == "reset":
            assert not opts, "stinky"
            args.engine.heading_counters = [None if e is None else 0 for e in args.engine.heading_counters]
            return

        if act == "pop":
            assert not opts, "stinky"
            raise NotImplementedError
            return
        
        if act == "push":
            raise NotImplementedError
        
        assert not opts.get("end") or not opts.get("depth"), "stinky"
        
        start = int(v) - 1 if (v := opts.get("start")) is not None else 0
        end = int(v) - 1 if (v := opts.get("end")) is not None else len(args.engine.heading_counters) - 1
        end = start + int(v) - 1 if (v := opts.get("depth")) is not None else end
        
        assert 0 <= start < len(args.engine.heading_counters) and 0 <= end < len(args.engine.heading_counters), "larp"
        assert start <= end, "nonsense"
        args.engine.heading_counters = [0 if start <= i < end else None for i in range(len(args.engine.heading_counters))]
        

    def _func_nest(self, args: ArgDirective.BaseArgs):
        args.engine.heading_offset += 1

    def _func_once(self, args: ArgDirective.BaseArgs):
        if args.engine.current_filegit in args.engine.fileset:
            # depleet current stream
            for l in args.engine.consume():
                pass
            else:
                args.engine.log_debug(f"file '{args.engine.current_file}' consumed (skipped)")

    def build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser("pragma", add_help=False, usage=argparse.SUPPRESS)
        subparsers = parser.add_subparsers()
        parsesr_hlevel = subparsers.add_parser("hlevel")
        parsesr_hlevel.add_argument("rest", nargs=argparse.REMAINDER)
        parsesr_hlevel.set_defaults(func=self._func_hlevel, parser=parsesr_hlevel)
        parsesr_nest = subparsers.add_parser("nest")
        parsesr_nest.set_defaults(func=self._func_nest, parser=parsesr_nest)
        parsesr_nest = subparsers.add_parser("once")
        parsesr_nest.set_defaults(func=self._func_once, parser=parsesr_nest)
        parser.set_defaults(parser=parser)
        return parser


class PageBreakDirective(Directive):
    """inserts page breaking feature"""

    trigger_on = ["pagebreak"]

    def handle(self, line, engine):
        # sketchy
        engine.feed_raw('<div style="break-after: always; page-break-after: always;"></div>\n') #<pdf:nextpage/>


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
