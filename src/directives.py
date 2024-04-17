import os
import re
from abc import ABC, abstractmethod
from io import TextIOWrapper, StringIO
from typing import Generator
import sys
from datetime import datetime

from engine import REGEX_IDENTIFIER, MACRO_ARG_SEPARATOR, Macro

class Directive(ABC):
    # arg regex (\s+(.+))?
    trigger_on: str = None

    @abstractmethod
    def handle(self, line: str, engine: 'BuildEngine') -> str | None:
        pass

class IncludeDirective(Directive):
    trigger_on = "include"

    def handle(self, line, engine):
        m = re.match(r'^#include \"(.+?)\"$', line)
        assert m, "malformed"
        
        filepath = m.group(1)

        assert engine.current_file
        
        filepath = os.path.normpath(os.path.join(os.path.dirname(engine.current_file), filepath))

        assert os.path.isfile(filepath), "file not found"
        assert filepath not in engine.filestack, "cyclic include"
        
        engine.filestack.append(filepath)

        engine.process_file(os.path.join(os.path.dirname(engine.current_file), m.group(1)))

        engine.filestack.pop()

class SectionDirective(Directive):
    trigger_on = "section"

    def handle(self, line, engine):
        m = re.match(r'^#section \"(.+?)\"$', line)
        assert m, "malformed"

        section_name = m.group(1)
        
        engine.sectionstack.append(section_name)

        engine.section_counters.append(1)
        
        print("hardcoded format")
        return "#" * len(engine.sectionstack) + f" {'.'.join([str(n) for n in engine.section_counters[0:-1]])}&nbsp;&nbsp;&nbsp;<strong>{section_name}</strong>\n"

class EndSectionDirective(Directive):
    trigger_on = "endsection"

    def handle(self, line, engine):
        assert len(engine.sectionstack) > 0, "no section to end"

        engine.section_counters.pop()
        engine.section_counters[-1] += 1

        engine.sectionstack.pop()


class CopyDirective(Directive):
    trigger_on = "copy"

    def handle(self, line, engine):
        m = re.match(r'^#copy \"(.+?)\" \"(.+?)\"$', line)
        assert m, "malformed"

        what_file = m.group(1)
        to_dir = m.group(2)

        src_file = os.path.join(os.path.dirname(engine.current_file), what_file)
        assert os.path.isfile(src_file), f"file {src_file} does not exist"
        
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
        return '<div style="page-break-before: always;"/>\n'  #<pdf:nextpage/>

class SetDirective(Directive):
    trigger_on = "set"
    
    def handle(self, line, engine):
        m = re.match(rf'^#set ({REGEX_IDENTIFIER}+) \"(.*?)\"$', line)
        assert m, "malformed"

        variable_name = m.group(1)
        variable_value = m.group(2)

        engine.variables[variable_name] = variable_value

class IncrementDirective(Directive):
    trigger_on = "increment"

    def handle(self, line, engine):
        m = re.match(rf'^#increment ({REGEX_IDENTIFIER}+) (-?\d+)$', line)
        assert m, "malformed"

        variable_name = m.group(1)
        by = m.group(2)

        assert variable_name in engine.variables, "undefined variable"

        value = int(engine.variables[variable_name])
        increment = int(by)

        engine.variables[variable_name] = str(value + increment)

class DefineDirective(Directive):
    trigger_on = "define"

    def handle(self, line, engine):
        m = re.match(rf'^#define ({REGEX_IDENTIFIER}+)(\(\s*{REGEX_IDENTIFIER}+\s*({MACRO_ARG_SEPARATOR}\s*{REGEX_IDENTIFIER}+\s*)*\))?', line)
        assert m, "malformed"

        macro_name = m.group(1)
        macro_params = m.group(2)

        assert macro_name not in engine.macros, "macro redefinition"

        m = Macro()
        m.params = None
        m.body = ""

        if macro_params:
            m.params = [x.strip() for x in macro_params.strip("()").split(MACRO_ARG_SEPARATOR)]
        
        for macro_line in engine.consume():
            if macro_line.startswith("#enddefine"):
                break
            m.body += macro_line
        else:
            assert False, "unended macro"
        engine.macros[macro_name] = m

class WarningDirective(Directive):
    trigger_on = "warning"

    def handle(self, line, engine):
        m = re.match(r'^#warning \"(.+?)\"$', line)
        assert m, "malformed"
        engine.log_warning(m.group(1))
