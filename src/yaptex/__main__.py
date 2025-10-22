motd = """
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

# TODO: simpler header indents
# TODO: header format

import os
from abc import ABC, abstractmethod
from io import TextIOWrapper, StringIO
from typing import Generator
import sys
from datetime import datetime
import argparse

from .engine import BuildEngine
from .renderers import *
from .log import *

def main():
    from .cli import build_parser

    parser = build_parser()
    args = parser.parse_args()

    log_print("░▀▄▀▒▄▀▄▒█▀▄░▀█▀▒██▀░▀▄▀ ™")
    log_print("░▒█▒░█▀█░█▀▒░▒█▒░█▄▄░█▒█")

    assert os.path.isfile(args.input)
    os.makedirs(args.output, exist_ok=True)
    #assert args.target in ["md", "html", "pdf"]

    builder = BuildEngine()

    build_dir = os.path.join(args.output, "raw")
    os.makedirs(build_dir, exist_ok=True)

    log_info("building...")
    builder.configure(pedantic=args.pedantic)
    try:
        try:
            raw_file = builder.build(args.input, build_dir,
                                     defines=[i for a in args.D for i in a] if args.D else None)
        except NotImplementedError as e:
            log_error("lazy fuck detection tripped")
            log_error(f"{type(e).__name__}: {str(e)}")
            raise
    except:
        log_error("build failed")
        
        if not args.verbose:
            exit(1)
        raise

    renderer_types = {}
    def add_renderer_type(rend: type[Renderer]):
        renderer_types[rend.identifier] = rend
    add_renderer_type(MdRenderer)
    add_renderer_type(HtmlRenderer)
    add_renderer_type(PdfRenderer)

    if (args.target != "raw"):
        def render_dependencies(renderer: Renderer, file: str):
            if renderer.depends_on:
                file = render_dependencies(renderer.depends_on(), file)
            log_info(f"renderer '{renderer.identifier}'")
            render_output = os.path.join(args.output, renderer.identifier)
            os.makedirs(render_output, exist_ok=True)
            return renderer.render(file, render_output)
        
        renderer = renderer_types[args.target]()

        log_info("rendering...")
        try:
            render_dependencies(renderer, raw_file)
        except:
            log_error("rendering failed")

            if not args.verbose:
                exit(1)
            raise

    log_info("done")
    
if __name__ == "__main__":
    main()
