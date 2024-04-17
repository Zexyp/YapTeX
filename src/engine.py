import os
import re
from abc import ABC, abstractmethod
from io import TextIOWrapper, StringIO
from typing import Generator
import sys
from datetime import datetime

import colorama

REGEX_IDENTIFIER: str = r'[a-zA-Z0-9_]'
MACRO_ARG_SEPARATOR: str = ";"

class Macro:
    params: list[str] = None
    body: str = None

from directives import *

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
            # TODO: IfDirective(),
        ]
        self.filestack: list[str] = []
        self.sectionstack: list[str] = []
        self.section_counters: list[int] = [1]
        self.macros: dict[str, Macro] = {}
        dtnow = datetime.now()
        self.variables: dict[str, str] = {
            "YEAR": str(dtnow.year),
            "MONTH": str(dtnow.month),
            "DAY": str(dtnow.day),
        }

        self.output: TextIOWrapper = None
        self.input: TextIOWrapper = None

        self.current_file: str = None
        self.current_line_number: str = None

    def build(self, source_file: str, output_dir: str = "./out"):
        assert os.path.isfile(source_file)
        assert os.path.isdir(output_dir)

        self.path_dir_source = os.path.dirname(source_file)
        self.path_dir_output = output_dir

        out_file = os.path.join(self.path_dir_output, "build.md")

        with open(out_file, mode='w', encoding="utf8") as file:
            try:
                self.output = file
                self.process_file(source_file)
                self.output = None
            except AssertionError as ex:
                self.log_error(f"- {self.current_file}:{self.current_line_number}: {ex}")
                raise
        
        if len(self.filestack) > 0:
            self.log_warning("wtf?!")

        return out_file

    def process(self, readable: TextIOWrapper):
        last_input = self.input
        self.input = readable

        for line in self.consume():
            self.feed(line)
        
        self.input = last_input

    def process_file(self, filepath):
        self.log_info(f"processing '{filepath}'")

        assert os.path.isfile(filepath), f"file {filepath} does not exist"

        with open(filepath, mode='r', encoding="utf8") as file:
            last_file = self.current_file

            self.current_file = filepath
            
            self.process(file)

            self.current_file = last_file
    
    def consume(self) -> Generator[str, None, None]:
        initial_sections_count = len(self.sectionstack)
        line_number = 0
        while line := self.input.readline():
            line_number += 1
            self.current_line_number = line_number
            yield line
        else:
            if len(self.sectionstack) != initial_sections_count:
                self.log_warning(f"unended sections {self.sectionstack}")
        
        self.current_line_number = None
        self.lines = None
        return None
    
    def handle_macro(self, macro_name: str, macro_args: str):
        self.log_directive(f"handle macro '{macro_name}{macro_args if macro_args else ''}'")
        
        assert macro_name in self.macros, "macro not defined"

        m = self.macros[macro_name]
        body = m.body
        
        if macro_args:
            args = [x.strip() for x in macro_args.strip("()").split(MACRO_ARG_SEPARATOR)]
            
            assert len(args) == len(m.params), "invalid number of arguments given"
            
            body = self.handle_variables(body, dict(zip(m.params, args)))
            
        result = self.process(StringIO(body))

        return result

    def feed(self, line: str):
        line = self.handle_variables(line, self.variables)

        if re.match(r'^#+ ', line):
            self.log_warning(f"- {self.current_file}:{self.current_line_number}: detected fixed header")
        elif line.startswith("#"):
            for d in self.directives:
                if line.startswith(f"#{d.trigger_on}"):
                    self.log_directive(line.strip('\n'))
                    line = d.handle(line, self)
                    break
            else:
                if m := re.match(rf'^#({"|".join(self.macros.keys())})(\s*\(\s*.+\s*(,\s*.+\s*)*\))?', line):
                    self.handle_macro(m.group(1), m.group(2))
                    return
                else:
                    self.log_warning(f"skipping unknown # ({line.strip('\n')})")
        
        if line:
            self.output.write(line)

    def handle_variables(self, body: str, vars: dict[str, str]):
        if not vars:
            return body

        def place_var(modifier, variable_name):

            assert variable_name in variable_name, "undefined variable"

            value = vars[variable_name]
            match modifier:
                case "bn":
                    value = os.path.basename(value)
                case "l":
                    value = value.lower()
                case "u":
                    value = value.upper()
                case "t":
                    value = value.title()
            
            return value
            
        return re.sub(rf'(bn|l|u|t)?%({"|".join(vars)})', lambda m: place_var(m.group(1), m.group(2)), body)

    def log_debug(self, msg: str):
        print(f"{colorama.Fore.LIGHTBLACK_EX}b: {msg}{colorama.Fore.RESET}")

    def log_directive(self, msg: str):
        print(f"{colorama.Fore.CYAN}d: {msg}{colorama.Fore.RESET}")

    def log_info(self, msg: str):
        print(f"i: {msg}")

    def log_error(self, msg: str):
        print(f"{colorama.Fore.RED}e: {msg}{colorama.Fore.RESET}")

    def log_warning(self, msg: str):
        print(f"{colorama.Fore.YELLOW}w: {msg}{colorama.Fore.RESET}")
