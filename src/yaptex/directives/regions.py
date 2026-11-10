"""did someone say see sharp?"""

import re

from . import Directive
from ..utils import str_unescape, REGEX_GROUP_QUOTED

class RegionDirective(Directive):
    """begine"""

    trigger_on = ["region"]

    def handle(self, line, engine):
        m = re.match(rf'^region\s+{REGEX_GROUP_QUOTED}$', line)
        engine.assert_match(m)

        section_name = str_unescape(m.group(1))

        engine.sectionstack.append(section_name)

        engine.feed_raw("#" * len(engine.sectionstack) + f" {section_name}\n")

class EndRegionDirective(Directive):
    """ende"""

    trigger_on = ["endregion"]

    def handle(self, line, engine):
        engine.assert_that(len(engine.sectionstack) > 0, "no section to end")

        engine.sectionstack.pop()
