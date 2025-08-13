from abc import abstractmethod

from yaptex.utils import *
from . import Directive


class BaseIfDirective(Directive):
    trigger_negative: str = None
    trigger_elif: str = None
    trigger_elif_negative: str = None
    trigger_else: str = None
    trigger_end: str = None

    def __init__(self):
        # convert to full representation
        self.trigger_negative = f"{DIRECTIVE_CHAR}{self.trigger_negative}"
        self.trigger_elif = f"{DIRECTIVE_CHAR}{self.trigger_elif}"
        self.trigger_elif_negative = f"{DIRECTIVE_CHAR}{self.trigger_elif_negative}"
        self.trigger_else = f"{DIRECTIVE_CHAR}{self.trigger_else}"
        self.trigger_end = f"{DIRECTIVE_CHAR}{self.trigger_end}"

    # build with mindset that negatives are longer
    def handle(self, line: str, engine: 'BuildEngine') -> str | None:
        negate_eval = line.startswith(self.trigger_negative)
        expression = line.removeprefix(self.trigger_negative).removeprefix(self.trigger_on).strip()
        eval_result = self.eval_condition(expression)
        eval_result = not eval_result if negate_eval else eval_result

        should_feed = True if eval_result else None

        del eval_result, negate_eval

        found_else = False
        for if_line in engine.consume():
            if if_line.startswith(self.trigger_end):
                engine.log_directive(if_line.strip('\n'))

                break

            if if_line.startswith(self.trigger_elif) or (negate_eval := if_line.startswith(self.trigger_elif_negative)):
                engine.log_directive(if_line.strip('\n'))

                if should_feed == False:
                    continue

                expression = if_line.removeprefix(self.trigger_elif_negative).removeprefix(self.trigger_elif).strip()
                eval_result = self.eval_condition(expression)
                eval_result = not eval_result if negate_eval else eval_result

                should_feed = True if eval_result else (None if should_feed is None else False)

                continue

            if if_line.startswith(self.trigger_else):
                engine.log_directive(if_line.strip('\n'))

                assert len(if_line.strip().removeprefix(self.trigger_else)) == 0, "malformed else"  # ends with new line
                assert not found_else, "multiple else statements"
                found_else = True

                if should_feed == False:
                    continue

                should_feed = should_feed is None

                continue

            if should_feed:
                engine.feed(if_line)
        else:
            assert False, "unended if"

    @abstractmethod
    def eval_condition(self, expression) -> bool:
        pass


class IfDirective(BaseIfDirective):
    trigger_on = "if"
    trigger_negative = "ifn"
    trigger_elif = "elif"
    trigger_elif_negative = "elifn"
    trigger_else = "else"
    trigger_end = "endif"

    def eval_condition(self, expression) -> bool:
        print(expression)


class IfDefDirective(BaseIfDirective):
    trigger_on = "ifdef"
    trigger_negative = "ifndef"
    trigger_elif = "elifdef"
    trigger_elif_negative = "elifndef"
    trigger_else = "else"
    trigger_end = "endif"

    def eval_condition(self, expression) -> bool:
        print(expression)