import re

from . import Directive
from ..utils import *

class RegionDirective(Directive):
    trigger_on = ["region"]

    def handle(self, line, engine):
        m = re.match(rf'^region\s+{REGEX_GROUP_QUOTED}$', line)
        if not m: raise MalformedError()

        section_name = str_unescape(m.group(1))

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