"""provide cli fucntionality"""

import argparse
import sys
import os
from importlib.metadata import version

from . import renderer_types
from .engine import BuildEngine
from .log import log_info, log_print, log_error, log_debug, color_activate, color_deactivate
from .renderers import Renderer
from . import fonts
from . import PATH_DIR_RESOURCE

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

    parser.add_argument("--version", action="version", version=f"YapTeX {version(__package__)}")
    parser.add_argument("--color", choices=["auto", "off", "force"], default="auto", help="usage of color in log")
    parser.add_argument("input", help="input file (use - for stdin as input)")
    parser.add_argument("--output", default="./out", help="output directory")
    parser.add_argument("--target", choices=["raw", "md", "html", "pdf"], default="raw", help="targeted output format")
    parser.add_argument("-D", nargs='*', action="append", help="additional defines")
    parser.add_argument("--pedantic", action="store_true", help="annoying yap")
    parser.add_argument("--verbose", action="store_true", help="yap on error")
    parser.add_argument("--rargs", default="", help="renderer args")

    prev_help = parser.print_help

    def help_hook(*args, **kwargs):
        sys.stdout.write(MOTD)
        prev_help(*args, **kwargs)

    parser.print_help = help_hook

    return parser

def build_font_parser():
    """build font arg parser"""
    
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()
    parser_font_pull = subparsers.add_parser("pull")
    parser_font_pull.add_argument("family", help="font family name")
    parser_font_pull.set_defaults(func=lambda args: fonts.download(args.family))
    parser_font_list = subparsers.add_parser("list", aliases=["ls"])
    def list_fonts():
        fonts_dir = os.path.join(PATH_DIR_RESOURCE, "font")
        print("\n".join([f for f in os.listdir(fonts_dir) if os.path.isdir(os.path.join(fonts_dir, f))]))
    parser_font_list.set_defaults(func=lambda args: list_fonts())

    return parser

def _render(raw_file, args):
    """no comment"""
    rargs = {}
    for a in args.rargs.strip().split(";"):
        a = a.strip()
        if a:
            pair = a.split("=")
            assert len(pair) == 2
            rargs[pair[0].strip()] = pair[1].strip()
    
    if rargs:
        log_debug(f"rargs:\n{'\n'.join([f'  {k}={v}' for k, v in rargs.items()])}")

    def render_dependencies(renderer: Renderer, file: str):
        """recursion"""

        if renderer.depends_on:
            file = render_dependencies(renderer.depends_on(), file)
        log_info(f"renderer '{renderer.identifier}'")
        render_output = os.path.join(args.output, renderer.identifier)
        os.makedirs(render_output, exist_ok=True)
        arg_ident = f"{renderer.identifier}:"
        return renderer.render(file, render_output, {k.removeprefix(arg_ident): v for k, v in rargs.items() if k.startswith(arg_ident)})

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

def _colorize(mode: str):
    if "NO_COLOR" in os.environ and len(os.environ["NO_COLOR"]):
        color_deactivate()
        log_debug("user does not wish for color")
    
    match mode:
        case "auto":
            (color_deactivate if sys.stdout.isatty() else color_activate)()
        case "off":
            color_deactivate()
        case "force":
            color_activate()
        case _:
            assert False, "invalid color mode"

def run():
    """make it move, used for cli"""

    parser = build_parser()

    args = parser.parse_args()

    _colorize(args.color)

    if args.color != "off":
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

def font():
    parser = build_font_parser()

    args = parser.parse_args()

    if args.func:
        args.func(args)
