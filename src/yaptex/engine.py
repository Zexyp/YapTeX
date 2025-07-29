import os
import re
from abc import ABC, abstractmethod
from io import TextIOWrapper, StringIO
from typing import Generator
import sys
from datetime import datetime
from typing import Callable

from .utils import *
from .log import *

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
            DefineDirective(),
            WarningDirective(),
            IfDirective(),
        ]
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
        }

        self.output: TextIOWrapper = None
        self.input: TextIOWrapper = None

        self.current_file: str = None
        self.current_line_number: str = None

    # build a file
    def build(self, source_file: str, output_dir: str):
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

    # processes readable stream
    def process(self, readable: TextIOWrapper):
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
            
            self.process(file)

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
    
    # fully handles a macro
    def handle_macro(self, macro_name: str, macro_args: str):
        self.log_directive(f"handle macro '{macro_name}{macro_args if macro_args else ''}'")
        
        assert macro_name in self.macros, "macro not defined"

        m = self.macros[macro_name]
        body = m.body
        
        if macro_args:
            args = [x.strip() for x in macro_args.strip("()").split(MACRO_ARG_SEPARATOR)]
            
            assert len(args) == len(m.params), "invalid number of arguments given"
            
            body = self.handle_variables(body, dict(zip(m.params, args)))
        
        try:
            # file context not possible due to relative paths
            result = self.process(StringIO(body))
        except:
            self.log_file_warning(f"during '{macro_name}' macro expansion an error occured")
            raise

        return result

    # adds line to be processed
    def feed(self, line: str):
        line = self.handle_variables(line, self.variables)

        if re.match(r'^#+ ', line):
            self.log_file_warning(f"detected fixed header") # pedantic
        elif line.startswith(PREPROCESSOR_CHAR):
            for d in self.directives:
                if line.startswith(f"{PREPROCESSOR_CHAR}{d.trigger_on}"):
                    self.log_directive(line.strip('\n'))
                    line = d.handle(line.removeprefix(PREPROCESSOR_CHAR), self)
                    break
            else:
                if m := re.match(rf'^{REGEX_MACRO_CHAR}({"|".join(self.macros.keys())})(\s*\(\s*.+\s*(,\s*.+\s*)*\))?', line):
                    self.handle_macro(m.group(1), m.group(2))
                    return
                else:
                    unknown = line.strip('\n')
                    self.log_warning(f"skipping unknown directive ({unknown})")

        if line:
            # hash escaping
            if line.startswith(f"{ESCAPE_CHAR}{PREPROCESSOR_CHAR}"):
                line = line.replace(f"{ESCAPE_CHAR}{PREPROCESSOR_CHAR}", PREPROCESSOR_CHAR, 1)
            
            self.output.write(line)

    # replaces variables with values
    def handle_variables(self, body: str, vars: dict[str, str]):
        if not vars:
            return body

        def place_var(modifier, variable_name):

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
                    value = re.sub('[^a-z ]', "", value.lower()).replace(" ", "-")
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
            
        return re.sub(rf'(id|html|esc|bn|dn|l|u|t)?%({"|".join(vars)})', lambda m: place_var(m.group(1), m.group(2)), body)

    # logging methods

    def format_file_position(self):
        return f"{self.current_file}:{self.current_line_number}"

    def log_debug(self, msg: str):
        log_debug(msg)

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

