import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import TextIOWrapper, StringIO
from typing import Generator
import sys
from datetime import datetime
from typing import Callable

from .utils import *
from .log import *

PER_LINE_VERBOSITY = False

@dataclass
class Macro:
    params: list[str] = None
    body: str = None

from .directives import *

class BuildEngine:
    def __init__(self) -> None:
        self.path_dir_output: str = "./out"
        self.path_dir_source: str = None;
        self.path_dir_resource: str = os.path.join(os.path.dirname(__file__), "res")

        self.directives: list[Directive] = [
            IncludeDirective(),
            SectionDirective(),
            EndSectionDirective(),
            CopyDirective(),
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
        ]
        self.directives.sort(reverse=True, key=lambda x: len(x.trigger_on)) # monkey fix, we need to handle longer names first
        self.filestack: list[str] = []
        self.sectionstack: list[str] = []
        self.section_counters: list[int] = [1]
        self.macros: dict[str, Macro] = {}
        dtnow = datetime.now()
        self.variables: dict[str, str | Callable] = {
            "_YEAR_": str(dtnow.year),
            "_MONTH_": str(dtnow.month),
            "_DAY_": str(dtnow.day),
            "__FILE__": lambda: self.current_file,
            "__LINE__": lambda: self.current_line_number,
            "__TIME__": lambda: str(dtnow.time),
            "__DATE__": lambda: str(dtnow.date),
        }

        self.output: TextIOWrapper = None
        self.input: TextIOWrapper = None

        self.current_file: str = None
        self.current_line_number: str = None

    # build a file
    def build(self, source_file: str, output_dir: str, defines: list[str] = None):
        if defines:
            self.log_debug("using supplied defines: " + ", ".join([f"'{v}'" for v in defines]))

        assert os.path.isfile(source_file)
        assert os.path.isdir(output_dir)

        self.path_dir_source = os.path.dirname(source_file)
        self.path_dir_output = output_dir

        out_file = os.path.join(self.path_dir_output, "index.md")

        with open(out_file, mode='w', encoding="utf8") as file:
            try:
                self.output = file
                self.process_file(source_file)
                self.output = None
            except AssertionError as ex:
                self.log_file_error(f"{ex}")
                raise

        if len(self.filestack) > 0:
            self.log_warning("wtf?!")

        return out_file

    def process_line(self, line):
        self.log_line("processing line: " + repr(line))
        if re.match(r'^#+ ', line):
            self.log_file_warning(f"detected fixed header")  # pedantic

        if line.startswith(DIRECTIVE_CHAR):
            for d in self.directives:
                if line.startswith(f"{DIRECTIVE_CHAR}{d.trigger_on}"):
                    line = line.strip('\n')
                    self.log_directive(line)
                    line = d.handle(line.removeprefix(DIRECTIVE_CHAR), self)

                    return ""

        if line:
            line = self.handle_variables(line, self.variables)
            line = self.handle_macros(line)

            # directive char escaping
            if line.startswith(f"{DIRECTIVE_ESCAPE_CHAR}{DIRECTIVE_CHAR}"):
                line = line.removeprefix(DIRECTIVE_ESCAPE_CHAR)

            return line

        return ""


    # processes readable stream
    def process_stream(self, readable: TextIOWrapper):
        last_input = self.input
        self.input = readable

        for line in self.consume():
            self.feed(line)

        self.input = last_input

    # opens a file and processes it
    def process_file(self, filepath):
        self.log_info(f"processing '{filepath}'")

        assert os.path.isfile(filepath), f"file {filepath} does not exist"

        with open(filepath, mode='r', encoding="utf8") as file:
            last_file = self.current_file

            self.current_file = filepath

            self.process_stream(file)

            self.current_file = last_file

    # reads a line from current file
    def consume(self) -> Generator[str, None, None]:
        initial_sections_count = len(self.sectionstack)
        line_number = 0
        while line := self.input.readline():
            line_number += 1
            self.current_line_number = line_number
            yield line
        else:
            if len(self.sectionstack) != initial_sections_count:
                self.log_warning(f"unended sections {self.sectionstack} (ignore this if in macro)")

        self.current_line_number = None
        self.lines = None
        return None

    # adds line to be processed
    def feed(self, line: str):
        line = self.process_line(line)
        assert line is not None
        self.log_line("writing: " + repr(line))
        self.output.write(line)

    # adds raw line
    def feed_raw(self, line: str):
        assert line is not None
        self.log_line("writing raw: " + repr(line))
        self.output.write(line)

    # replaces variables with values
    def handle_variables(self, body: str, vars: dict[str, str]):
        if not vars:
            return body

        def place_variable(modifier, variable_name):

            assert variable_name in variable_name, "undefined variable"

            value = vars[variable_name]
            if callable(value):
                self.log_debug(f"called variable '{variable_name}'")
                value = value()

            match modifier:
                case "html":
                    import html
                    value = html.escape(value)
                case "id":
                    value = re.sub('[^a-zA-Z0-9 ]', "", value.lower()).replace(" ", "-")
                case "esc":
                    value = str_escape(value)
                case "bn":
                    value = os.path.basename(value)
                case "dn":
                    value = os.path.dirname(value)
                case "l":
                    value = value.lower()
                case "u":
                    value = value.upper()
                case "t":
                    value = value.title()

            return value

        pattern = rf'(id|html|esc|bn|dn|l|u|t)?%({"|".join([re.escape(vn) for vn in vars])})'
        result = re.sub(pattern, lambda m: place_variable(m.group(1), m.group(2)), body)
        if VARIABLE_CHAR in result:
            self.log_file_warning(f"unresolved variable")
        return result

    def handle_macros(self, line) -> str:
        self.log_line("line for macro handling: " + repr(line))
        # fully handles a macro
        def place_macro(macro_name: str, macro_args: str):
            self.log_debug(f"handle macro '{macro_name}{macro_args if macro_args else ''}'")

            assert macro_name in self.macros, f"macro '{macro_name}' not defined"

            m = self.macros[macro_name]
            body = m.body

            if macro_args:
                args = [x.strip() for x in macro_args.strip("()").split(MACRO_ARG_SEPARATOR)]

                assert len(args) == len(m.params), "invalid number of arguments given"

                body = self.handle_variables(body, dict(zip(m.params, args)))

            result = ""
            if body:
                try:
                    # file context not possible due to relative paths
                    result = self.process_line(body)
                except:
                    self.log_file_warning(f"during '{macro_name}' macro expansion an error occurred")
                    raise

            return result

        pattern = rf'{REGEX_MACRO_CHAR}({"|".join([re.escape(mn) for mn in self.macros.keys()])})(\s*\(\s*.+\s*({MACRO_ARG_SEPARATOR}\s*.+\s*)*\))?'
        result = re.sub(pattern, lambda m: place_macro(m.group(1), m.group(2)), line)
        if MACRO_CHAR in result:
            self.log_file_warning(f"unresolved macro")

        return result

    # logging methods

    def assert_that(self, condition):
        raise NotImplemented

    def format_file_position(self):
        return f"{self.current_file}:{self.current_line_number}"

    def log_debug(self, msg: str):
        log_debug(msg)

    def log_line(self, msg: str):
        if (PER_LINE_VERBOSITY): self.log_debug(f"l: {msg}")

    def log_directive(self, msg: str):
        log_directive(msg)

    def log_info(self, msg: str):
        log_info(msg)

    def log_error(self, msg: str):
        log_error(msg)

    def log_warning(self, msg: str):
        log_warning(msg)

    def log_file_error(self, msg: str):
        self.log_error(f"- {self.format_file_position()}: {msg}")

    def log_file_warning(self, msg: str):
        self.log_warning(f"- {self.format_file_position()}: {msg}")

