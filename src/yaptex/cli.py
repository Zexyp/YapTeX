"""provide cli fucntionality"""

import argparse
import sys
import os
from importlib.metadata import version

from . import renderer_types
from .engine import BuildEngine
from .log import log_info, log_print, log_error
from .renderers import Renderer

MOTD = """
                                                             ™
▀███▀   ▀██▀                 ███▀▀██▀▀███       ▀███▀   ▀██▀ 
  ███   ▄█                   █▀   ██   ▀█         ███▄  ▄█   
   ███ ▄█   ▄█▀██▄ ▀████████▄     ██      ▄▄█▀██   ▀██▄█▀    
    ████   ██   ██   ██   ▀██     ██     ▄█▀   ██    ███     
     ██     ▄█████   ██    ██     ██     ██▀▀▀▀▀▀  ▄█▀▀██▄   
     ██    ██   ██   ██   ▄██     ██     ██▄    ▄ ▄█   ▀██▄  
   ▄████▄  ▀████▀██▄ ██████▀    ▄████▄    ▀█████▀██▄▄  ▄▄███▄
                     ██                                      
                   ▄████▄                                    
The Markdow Preprocessor

"""

def build_parser():
    """build arg parser"""

    parser = argparse.ArgumentParser()

    parser.add_argument('--version', action='version', version=f"YapTeX {version(__package__)}")
    parser.add_argument("input", help="use - for stdin as input")
    parser.add_argument("--output", default="./out", help="output directory")
    parser.add_argument("--target", choices=["raw", "md", "html", "pdf"], default="raw", help="targeted output format")
    parser.add_argument("-D", nargs='*', action="append", help="additional defines")
    parser.add_argument("--pedantic", action="store_true", help="annoying yap")
    parser.add_argument("--verbose", action="store_true", help="yap on error")

    prev_help = parser.print_help

    def help_hook(*args, **kwargs):
        sys.stdout.write(MOTD)
        prev_help(*args, **kwargs)

    parser.print_help = help_hook

    #subparsers = parser.add_subparsers()
    #parser_font = subparsers.add_parser("font")
    #parser_font.add_subparsers().add_parser("pull")

    return parser

def _render(raw_file, args):
    """no comment"""

    def render_dependencies(renderer: Renderer, file: str):
        """recursion"""

        if renderer.depends_on:
            file = render_dependencies(renderer.depends_on(), file)
        log_info(f"renderer '{renderer.identifier}'")
        render_output = os.path.join(args.output, renderer.identifier)
        os.makedirs(render_output, exist_ok=True)
        return renderer.render(file, render_output)

    renderer = renderer_types[args.target]()

    render_dependencies(renderer, raw_file)

def _build(args):
    """no comment"""

    os.makedirs(args.output, exist_ok=True)

    builder = BuildEngine()

    build_dir = os.path.join(args.output, "raw")
    os.makedirs(build_dir, exist_ok=True)

    builder.configure(pedantic=args.pedantic)

    try:
        raw_file = builder.build(args.input, build_dir,
                                    defines=[i for a in args.D for i in a] if args.D else None)
    except NotImplementedError as e:
        log_error("lazy fuck detection tripped")
        log_error(f"{type(e).__name__}: {str(e)}")
        raise

    return raw_file

def run():
    """make it move, used for cli"""

    parser = build_parser()

    args = parser.parse_args()

    log_print("░▀▄▀▒▄▀▄▒█▀▄░▀█▀▒██▀░▀▄▀ ™")
    log_print("░▒█▒░█▀█░█▀▒░▒█▒░█▄▄░█▒█")

    log_info("building...")
    try:
        raw_file = _build(args)
    except:
        log_error("build failed")

        if not args.verbose:
            sys.exit(1)
        raise

    if args.target != "raw":
        log_info("rendering...")
        try:
            _render(raw_file, args)
        except:
            log_error("rendering failed")

            if not args.verbose:
                sys.exit(1)
            raise

    log_info("done")
