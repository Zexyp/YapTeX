import argparse
import sys
from .__main__ import motd

def build_parser():
    parser = argparse.ArgumentParser()

    from importlib.metadata import version
    parser.add_argument('--version', action='version', version=f"YapTeX {version(__package__)}")
    parser.add_argument("input", help="use - for stdin as input")
    parser.add_argument("--output", default="./out", help="output directory")
    parser.add_argument("--target", choices=["raw", "md", "html", "pdf"], default="raw", help="targeted output format")
    parser.add_argument("-D", nargs='*', action="append", help="additional defines")
    parser.add_argument("--pedantic", action="store_true", help="annoying yap")
    parser.add_argument("--verbose", action="store_true", help="yap on error")

    prev_help = parser.print_help

    def help_hook(*args, **kwargs):
        sys.stdout.write(motd)
        prev_help(*args, **kwargs)

    parser.print_help = help_hook

    subparsers = parser.add_subparsers()
    parser_font = subparsers.add_parser("font")
    parser_font.add_subparsers().add_parser("pull")

    return parser

def run():
    parser = build_parser()
    raise NotImplementedError
