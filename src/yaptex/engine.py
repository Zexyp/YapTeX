"""home of main machinery"""

# TODO: import logging
from io import TextIOWrapper
from typing import Callable, Generator
from collections import OrderedDict
from datetime import datetime
import html
import sys
import os
import re

import yaml

from . import utils
from .utils import str_escape, REGEX_ESCAPE_CHAR, PAGE_HEADER_SEPARATOR, REGEX_VARIABLE_CHAR, VARIABLE_FORMAT_SEPARATOR, VARIABLE_CHAR, REGEX_MACRO_CHAR, MACRO_CHAR, ESCAPE_CHAR, DIRECTIVE_CHAR, REGEX_IDENTIFIER, MACRO_ARG_SEPARATOR
from .log import log_debug, log_warning, log_error, log_directive, log_info
from .structures import Macro
from .errors import YapTeXError, BuildError, BuildFileNotFoundError, MalformedError
from .directives import *

PER_LINE_VERBOSITY = False

class BuildEngine:
    """main machinery"""
    def __init__(self) -> None:
        self.path_dir_output: str = "./out"
        self.path_dir_source: str = None
        self.path_dir_resource: str = os.path.join(os.path.dirname(__file__), "res")

        self.directives: list[Directive] = [
            IncludeDirective(),

            RegionDirective(),
            EndRegionDirective(),
            PageBreakDirective(),

            SetDirective(),
            IncrementDirective(),
            DecrementDirective(),

            DefineDirective(),
            UndefineDirective(),

            IfDirective(),
            IfDefDirective(),

            WarningDirective(),
            ErrorDirective(),

            CopyDirective(),

            LineDirective(),
            EmbedDirective(),
        ]
        self.directives_map: OrderedDict[str, Directive] = None
        def build_directives_map():
            self.directives_map = OrderedDict()

            for directive in self.directives:
                for key in directive.trigger_on:
                    assert key not in self.directives_map, f"overlapping directives '{key}'"
                    self.directives_map[key] = directive

            self.directives_map = OrderedDict(sorted(self.directives_map.items(), key=lambda item:  item[0], reverse=True))
        build_directives_map()

        self.filestack: list[str] = []
        self.sectionstack: list[str] = []
        self.section_counters: list[int] = [1]
        self.macros: dict[str, Macro] = {
            "sizeof": Macro(params=None, body=None, action=lambda args, engine: engine.feed(str(len(args[0])))),
        }
        dtnow = datetime.now()
        self.variables: dict[str, str | Callable] = {
            "_YEAR_": str(dtnow.year),
            "_MONTH_": str(dtnow.month),
            "_DAY_": str(dtnow.day),
            "__FILE__": lambda: self.current_file_alias or self.current_file,
            "__LINE__": lambda: str(self.current_file_line_number),
            "__TIME__": str(dtnow.time()),
            "__DATE__": str(dtnow.date()),
        }

        self.output: TextIOWrapper = None
        self.input: TextIOWrapper = None

        self.current_file: str = None
        self.current_file_line_number: int = None
        self.current_file_alias: str | None = None

        self.pedantic = False

        self.format_modifiers: dict[str, Callable[[str], str]] = {
            "html": html.escape,
            "slug": utils.slugify,
            "esc": str_escape,
            "bn": os.path.basename,
            "dn": os.path.dirname,
            "l": str.lower,
            "u": str.upper,
            "t": str.title,
        }

    def configure(self, pedantic: bool = None):
        """sigh"""
        if pedantic is not None:
            self.pedantic = pedantic

    # build a file
    def build(self, source_file: str, output_dir: str,
              defines: list[str] = None):
        """build file and do some outputing"""

        if defines:
            self.log_debug("using supplied defines: " + ", ".join([f"'{v}'" for v in defines]))
            for k in defines:
                m = Macro()
                m.body = None
                m.params = None
                self.macros[k] = m

        if not os.path.isdir(output_dir):
            raise BuildFileNotFoundError(f"not a dir '{output_dir}'")

        self.path_dir_source = os.path.dirname(source_file) if os.path.isfile(source_file) else os.getcwd()
        self.path_dir_output = output_dir

        out_file = os.path.join(self.path_dir_output, "index.md")

        with open(out_file, mode='w', encoding="utf8") as file:
            try:
                self.output = file
                self.process_file(source_file)
                self.output = None
            except YapTeXError as ex:
                self.log_file_error(f"{ex}")
                raise

        if len(self.filestack) > 0:
            self.log_warning("wtf?!")

        return out_file

    # handle all stuff on line
    def process_line(self, line):
        """just processes a line"""

        assert line is not None

        self.log_line("processing line: " + repr(line))

        # pedantic
        if re.match(r'^#+ ', line):
            self.pedantic_log_file("detected fixed header")

        line = self.handle_variables(line, self.variables)

        if line.startswith(DIRECTIVE_CHAR):
            return self.handle_directive(line)

        line = self.handle_macros(line)

        # dynamic headering, dynheader
        if re.match(r'^-(#+) ', line):
            self.log_debug("dynheader")
            line = len(self.sectionstack) * "#" + line.removeprefix("-")

        # directive char escaping
        if line.startswith(f"{ESCAPE_CHAR}{DIRECTIVE_CHAR}"):
            line = line.removeprefix(ESCAPE_CHAR)
        # dynheader escaping
        if re.match(rf'^{REGEX_ESCAPE_CHAR}-(#+) ', line):
            line = line.removeprefix(ESCAPE_CHAR)

        return line

    # execute a directive
    def handle_directive(self, line):
        """is magical"""
        m = re.match("^#([a-z]+)", line)
        if m:
            directive_key = m.group(1)
            if directive_key not in self.directives_map:
                self.pedantic_log_file(f"unknown directive '{directive_key}'")
                return line
            self.log_directive(line.removesuffix("\n"))
            directive = self.directives_map[directive_key]
            directive.handle(line.removeprefix(DIRECTIVE_CHAR), self)
            return ""

        # possible header
        if not line.startswith(f"{DIRECTIVE_CHAR} "):
            self.pedantic_log_file("unreadable directive")

        return line

    # processes readable stream
    def process_stream(self, readable: TextIOWrapper):
        """works on stream"""

        last_input = self.input
        self.input = readable

        first_line = True

        # page header
        reading_page_header = None # states: None = don't care; True = start was found, now reading; False = read ended
        page_header_string = ""

        last_line = None
        for line in self.consume():
            last_line = line

            # first line header start handling
            if first_line:
                first_line = False

                if line.startswith(PAGE_HEADER_SEPARATOR):
                    self.log_debug("page header started")
                    reading_page_header = True
                    continue # skip this line

            # header eating
            if reading_page_header == True:
                if line.startswith(PAGE_HEADER_SEPARATOR):
                    reading_page_header = False
                    self.log_debug("parsing page header")
                    print(yaml.safe_load(page_header_string))
                    raise NotImplementedError
                    continue # skip this line
                page_header_string += line # eat
                continue

            self.feed(line)
        
        if last_line is not None and not last_line.endswith("\n"):
            self.pedantic_log_file("no new line at the end of file")

        self.input = last_input

    # opens a file and processes it
    def process_file(self, filepath):
        """processes stream of give file path"""

        self.log_info(f"processing '{filepath}'")

        if filepath == "-":
            stream = sys.stdin
        else:
            assert os.path.isfile(filepath), f"file '{filepath}' does not exist"
            stream = open(filepath, mode='r', encoding="utf8")

        with stream as file:
            last_file = self.current_file
            last_line = self.current_file_line_number

            self.current_file = filepath
            #self.current_file_line_number (is set in process stream)
            self.filestack.append(filepath)

            self.process_stream(file)

            self.current_file = last_file
            self.current_file_line_number = last_line
            self.filestack.pop()

    # reads a line from current file
    def consume(self) -> Generator[str, None, None]:
        """\"nom nom\", *consumes line cutely*"""
        initial_sections_count = len(self.sectionstack)
        self.current_file_line_number = 0
        while line := self.input.readline():
            self.current_file_line_number += 1
            yield line
        else:
            if len(self.sectionstack) != initial_sections_count:
                self.log_warning(f"unended sections: {", ".join(f"'{s}'" for s in self.sectionstack)} (ignore this if in macro)")

        self.current_file_line_number = None
        return None

    # adds line to be processed
    def feed(self, line: str):
        """*gulps cutely*, places a line to ouptut"""
        assert line is not None
        line = self.process_line(line)
        assert line is not None
        self.log_line("writing: " + repr(line))
        self.output.write(line)

    # adds raw
    def feed_raw(self, line: str):
        """shoving mechanism"""
        assert line is not None
        self.log_line("writing raw: " + repr(line))
        self.output.write(line)

    # replaces variables with their values
    def handle_variables(self, body: str, vrbls: dict[str, str]) -> str:
        """put vars"""
        if not vrbls:
            return body

        def place_variable(match):
            variable_name = match.group(2) or match.group(3)
            modifier = match.group(4)

            self.log_debug(f"handle variable '{variable_name}'{f" (format: {modifier})" if modifier else ""}")

            if variable_name not in vrbls:
                self.log_debug(f"variable '{variable_name}' is not defined")
                return match.group()

            value = vrbls[variable_name]
            if callable(value):
                self.log_debug("called variable '{variable_name}'")
                value = value()

            if modifier:
                self.assert_that(modifier in self.format_modifiers, f"unknown format modifier '{modifier}'")
                value = self.format_modifiers[modifier](value)

            return value

        # for now all modifiers are lowercase
        # fixme: merge subs
        pattern = rf'{REGEX_VARIABLE_CHAR}(({REGEX_IDENTIFIER})|{{({REGEX_IDENTIFIER})(?:{VARIABLE_FORMAT_SEPARATOR}([a-z]+))?}})'
        result = re.sub(rf'(?<!{REGEX_ESCAPE_CHAR})' + pattern, place_variable, body)
        # cleanup
        result = re.sub(rf'{REGEX_ESCAPE_CHAR}({pattern})', r'\1', result)

        if VARIABLE_CHAR in result:
            self.log_file_warning("scareware: unresolved variable?")

        return result

    # handles macros on line
    def handle_macros(self, line) -> str:
        """put macros"""
        self.log_line("line for macro handling: " + repr(line))
        # fully handles a macro
        def place_macro(macro_name: str, macro_args: str):
            self.log_debug(f"handle macro '{macro_name}{macro_args if macro_args else ''}'")

            if not macro_name in self.macros:
                raise BuildError(f"macro '{macro_name}' not defined")

            m = self.macros[macro_name]
            body = m.body
            action = m.action

            try:
                if macro_args:
                    # clean and split args
                    args = [x.strip() for x in macro_args.strip("()").split(MACRO_ARG_SEPARATOR)]

                    self.assert_that(len(args) == len(m.params), "invalid number of arguments given")

                    # action fuckery
                    if action:
                        assert body is None, "unusable body"
                        action(args, self)
                    elif body is not None:
                        body = self.handle_variables(body, dict(zip(m.params, args)))
                    else:
                        assert False, "useless macro"

                if body:
                    # file context not possible due to relative paths
                    for body_line in re.split(r'(\n)', body):
                        self.feed(body_line)
            except:
                self.log_file_warning(f"during '{macro_name}' macro expansion an error occurred")
                raise

            return "" # does not return anything usable

        # TODO: kwargs
        # fixme: merge subs
        pattern = rf'{REGEX_MACRO_CHAR}({REGEX_IDENTIFIER})(\(\s*.+\s*({MACRO_ARG_SEPARATOR}\s*.+\s*)*\))?'
        result = re.sub(rf'(?<!{REGEX_ESCAPE_CHAR})' + pattern, lambda m: place_macro(m.group(1), m.group(2)), line)
        # cleanup
        result = re.sub(rf'{REGEX_ESCAPE_CHAR}({pattern})', r'\1', result)

        if MACRO_CHAR in result:
            self.log_file_warning(f"scareware: unresolved macro?")

        return result

    # assets

    def assert_match(self, m):
        """custom assert thingy"""
        if not m:
            raise MalformedError("malformed")

    def assert_file(self, file):
        """custom assert thingy"""
        if not os.path.isfile(file):
            raise BuildFileNotFoundError(f"file '{file}' does not exist")

    def assert_directory(self, directory):
        """custom assert thingy"""
        if not os.path.isdir(directory):
            raise BuildFileNotFoundError(f"directory '{directory}' does not exist")

    def assert_that(self, condition, msg=""):
        """custom assert thingy"""
        if not condition:
            raise BuildError(msg)

    # logging methods

    def _format_file_position(self):
        return f"{self.current_file}:{self.current_file_line_number}"

    def _format_file_msg(self, msg):
        return f"- {self._format_file_position()}: {msg}"

    def log_debug(self, msg: str):
        """engine log"""
        log_debug(msg)

    def log_line(self, msg: str):
        """high debug thingy"""
        if PER_LINE_VERBOSITY:
            self.log_debug(f"eng: l: {msg}")

    def log_directive(self, msg: str):
        """engine log"""
        log_directive(f"eng: {msg}")

    def log_info(self, msg: str):
        """engine log"""
        log_info(f"eng: {msg}")

    def log_error(self, msg: str):
        """engine log"""
        log_error(f"eng: {msg}")

    def log_warning(self, msg: str):
        """engine log"""
        log_warning(f"eng: {msg}")

    def log_file_error(self, msg: str):
        """engine log"""
        self.log_error(self._format_file_msg(msg))

    def log_file_warning(self, msg: str):
        """engine log"""
        self.log_warning(self._format_file_msg(msg))

    def pedantic_log(self, msg: str):
        """engine log"""
        if self.pedantic:
            self.log_warning(f"ped: {msg}")

    def pedantic_log_file(self, msg: str):
        """engine log"""
        self.pedantic_log(self._format_file_msg(msg))
