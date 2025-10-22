import io
from typing import Callable
from collections import OrderedDict
import html
# TODO: import logging

import yaml

from . import directives
from .utils import *
from .log import *
from .structures import Macro

PER_LINE_VERBOSITY = False

from .directives import *

class BuildEngine:
    def __init__(self) -> None:
        self.path_dir_output: str = "./out"
        self.path_dir_source: str = None;
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
            "html": lambda v: html.escape(v),
            "id": lambda v: re.sub('[^a-zA-Z0-9 ]', "", v.lower()).replace(" ", "-"),
            "esc": lambda v: str_escape(v),
            "bn": lambda v: os.path.basename(v),
            "dn": lambda v: os.path.dirname(v),
            "l": lambda v: v.lower(),
            "u": lambda v: v.upper(),
            "t": lambda v: v.title(),
        }

    def configure(self, pedantic: bool = None):
        if pedantic is not None: self.pedantic = pedantic

    # build a file
    def build(self, source_file: str, output_dir: str,
              defines: list[str] = None):
        if defines:
            self.log_debug("using supplied defines: " + ", ".join([f"'{v}'" for v in defines]))
            for k in defines:
                m = Macro()
                m.body = None
                m.params = None
                self.macros[k] = m

        assert os.path.isfile(source_file), f"not a file '{source_file}'"
        assert os.path.isdir(output_dir), f"not a dir '{output_dir}'"

        self.path_dir_source = os.path.dirname(source_file)
        self.path_dir_output = output_dir

        out_file = os.path.join(self.path_dir_output, "index.md")

        with open(out_file, mode='w', encoding="utf8") as file:
            try:
                self.output = file
                self.process_file(source_file)
                self.output = None
            # TODO: better assertion
            except AssertionError as ex:
                self.log_file_error(f"{ex}")
                raise

        if len(self.filestack) > 0:
            self.log_warning("wtf?!")

        return out_file

    # handle all stuff on line
    def process_line(self, line):
        self.log_line("processing line: " + repr(line))

        # pedantic
        if re.match(r'^#+ ', line):
            self.pedantic_log_file(f"detected fixed header")

        if line.startswith(DIRECTIVE_CHAR):
            return self.handle_directive(line)

        if not line:
            return ""

        line = self.handle_variables(line, self.variables)
        line = self.handle_macros(line)

        # directive char escaping
        if line.startswith(f"{DIRECTIVE_ESCAPE_CHAR}{DIRECTIVE_CHAR}"):
            line = line.removeprefix(DIRECTIVE_ESCAPE_CHAR)

        return line

    # execute a directive
    def handle_directive(self, line):
        m = re.match("^#([a-z]+)", line)
        if m:
            directive_key = m.group(1)
            if directive_key not in self.directives_map:
                self.pedantic_log_file(f"unknown directive '{directive_key}'")
                return line
            log_directive(line.removesuffix("\n"))
            directive = self.directives_map[directive_key]
            directive.handle(line.removeprefix(DIRECTIVE_CHAR), self)
            return ""

        # possible header
        elif not line.startswith(f"{DIRECTIVE_CHAR} "):
            self.pedantic_log_file("unreadable directive")

        return line

    # processes readable stream
    def process_stream(self, readable: TextIOWrapper):
        last_input = self.input
        self.input = readable

        first_line = True

        # page header
        reading_page_header = None # states: None = don't care; True = start was found, now reading; False = read ended
        page_header_string = ""

        for line in self.consume():
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

        self.input = last_input

    # opens a file and processes it
    def process_file(self, filepath):
        self.log_info(f"processing '{filepath}'")

        assert os.path.isfile(filepath), f"file '{filepath}' does not exist"

        with open(filepath, mode='r', encoding="utf8") as file:
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
        initial_sections_count = len(self.sectionstack)
        self.current_file_line_number = 0
        while line := self.input.readline():
            self.current_file_line_number += 1
            yield line
        else:
            if len(self.sectionstack) != initial_sections_count:
                self.log_warning(f"unended sections {self.sectionstack} (ignore this if in macro)")

        self.current_file_line_number = None
        return None

    # adds line to be processed
    def feed(self, line: str):
        line = self.process_line(line)
        assert line is not None
        self.log_line("writing: " + repr(line))
        self.output.write(line)
    
    # adds raw
    def feed_raw(self, line: str):
        assert line is not None
        self.log_line("writing raw: " + repr(line))
        self.output.write(line)

    # replaces variables with their values
    def handle_variables(self, body: str, vars: dict[str, str]) -> str:
        if not vars:
            return body

        def place_variable(variable_name, modifier):

            assert variable_name in vars, f"variable '{variable_name}' not defined"

            value = vars[variable_name]
            if callable(value):
                self.log_debug(f"called variable '{variable_name}'")
                value = value()

            if modifier:
                assert modifier in self.format_modifiers, f"unknown format modifier '{modifier}'"
                value = self.format_modifiers[modifier](value)

            return value

        # for now all modifiers are lowercase
        # fixme: merge subs
        pattern = rf'(?<!{REGEX_ESCAPE_CHAR}){REGEX_VARIABLE_CHAR}(({REGEX_IDENTIFIER})|{{({REGEX_IDENTIFIER})(?:{VARIABLE_FORMAT_SEPARATOR}([a-z]+))?}})'
        result = re.sub(pattern, lambda m: place_variable(m.group(2) or m.group(3), m.group(4)), body)
        # cleanup
        result = re.sub(rf'{REGEX_ESCAPE_CHAR}({pattern})', r'\1', result)

        if VARIABLE_CHAR in result:
            self.log_file_warning(f"scareware: unresolved variable")

        return result

    # handles macros on line
    def handle_macros(self, line) -> str:
        self.log_line("line for macro handling: " + repr(line))
        # fully handles a macro
        def place_macro(macro_name: str, macro_args: str):
            self.log_debug(f"handle macro '{macro_name}{macro_args if macro_args else ''}'")

            assert macro_name in self.macros, f"macro '{macro_name}' not defined"

            m = self.macros[macro_name]
            body = m.body
            action = m.action

            try:
                if macro_args:
                    # clean and split args
                    args = [x.strip() for x in macro_args.strip("()").split(MACRO_ARG_SEPARATOR)]

                    assert len(args) == len(m.params), "invalid number of arguments given"

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
        pattern = rf'(?<!{REGEX_ESCAPE_CHAR}){REGEX_MACRO_CHAR}({REGEX_IDENTIFIER})(\s*\(\s*.+\s*({MACRO_ARG_SEPARATOR}\s*.+\s*)*\))?'
        result = re.sub(pattern, lambda m: place_macro(m.group(1), m.group(2)), line)
        # cleanup
        result = re.sub(rf'{REGEX_ESCAPE_CHAR}({pattern})', r'\1', result)

        if MACRO_CHAR in result:
            self.log_file_warning(f"scareware: unresolved macro")

        return result

    # logging methods

    def assert_that(self, condition):
        raise NotImplemented

    def format_file_position(self):
        return f"{self.current_file}:{self.current_file_line_number}"

    def format_file_msg(self, msg):
        return f"- {self.format_file_position()}: {msg}"

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
        self.log_error(self.format_file_msg(msg))

    def log_file_warning(self, msg: str):
        self.log_warning(self.format_file_msg(msg))

    def pedantic_log(self, msg: str):
        if self.pedantic: self.log_warning(msg)

    def pedantic_log_file(self, msg: str):
        self.pedantic_log(self.format_file_msg(msg))

