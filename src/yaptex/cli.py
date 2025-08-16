import argparse
import os, sys
from .__main__ import motd

def build_parser():
    parser = argparse.ArgumentParser()

    from importlib.metadata import version
    parser.add_argument('--version', action='version', version=f"YapTeX {version(__package__)}")
    parser.add_argument("input")
    parser.add_argument("--output", default="./out", help="output directory")
    parser.add_argument("--target", choices=["raw", "md", "html", "pdf"], default="raw", help="targeted output format")
    parser.add_argument("-D", nargs='*', action="append", help="additional defines")
    parser.add_argument("--pedantic", action="store_true", help="annoying yap")

    prev_help = parser.print_help

    def help_hook(*args, **kwargs):
        sys.stdout.write(motd)
        prev_help(*args, **kwargs)

    parser.print_help = help_hook

    return parser

def run():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_font = subparsers.add_parser("font")
    parser_font.add_subparsers().add_parser("pull")

# state of progress
_last_progress_total: int | None = None
_progress_update = 1000 # in ms

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=80, width=None, fill='█', empty='-', format='\r{prefix} |{bar}| {percentage}% {suffix}', finish=None):
    """it's not just stolen, i also modified and improved this"""
    percentage_length = 3 + 1 + decimals

    if width is None and sys.stdout.isatty():
        width = os.get_terminal_size().columns
    if width:
        junk_length = len(re.sub(r'\{.*?\}', '', format)) + len(prefix) + len(suffix) + percentage_length
        length = max(width - junk_length, 0)

    if total:
        percentage_value = 100 * (iteration / float(total))
        percentage = f"{percentage_value:.{decimals}f}".rjust(percentage_length)
        filled_length = min(length, int(length * iteration // total))
    else:
        percentage = "-".rjust(percentage_length)
        filled_length = 0

    bar = fill * filled_length + empty * (length - filled_length)

    line = format.format(prefix=prefix, bar=bar, percentage=percentage, suffix=suffix)
    print(line, end="\r")

    # print new line on complete
    if iteration == total and finish is None:
        print()

    if finish:
        print()


def progress_start(total):
    """used to initialize progress bar"""
    if not _progress_update:
        return
    global _last_progress_total
    assert _last_progress_total is None
    _last_progress_total = total
    print_progress_bar(0, _last_progress_total, prefix=f"Preparing...:", finish=False)


def progress_update(iteration):
    """update state"""
    if not _progress_update:
        return
    global _last_progress_total
    assert _last_progress_total is not None
    if iteration > _last_progress_total:
        _last_progress_total = iteration
    if iteration % _progress_update != 0:
        return
    print_progress_bar(iteration, _last_progress_total, prefix=f"Working... ({str(iteration).rjust(len(str(_last_progress_total)))}/{_last_progress_total}):", finish=False)


def progress_finish():
    """fill progress bar and reset context"""
    if not _progress_update:
        return
    global _last_progress_total
    assert _last_progress_total is not None
    print_progress_bar(_last_progress_total, _last_progress_total, prefix=f"Done ({_last_progress_total}/{_last_progress_total}):", finish=True)
    _last_progress_total = None