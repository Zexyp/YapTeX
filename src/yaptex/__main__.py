yaptex_motd = """
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
    parser = argparse.ArgumentParser()

    from importlib.metadata import version
    parser.add_argument('--version', action='version', version=f"YapTeX {version(__package__)}")
    parser.add_argument("input")
    parser.add_argument("--output", default="./out")
    parser.add_argument("--target", choices=["raw", "md", "html", "pdf"], default="raw")
    parser.add_argument("-D", nargs='*', action="append")
    parser.add_argument("--pedantic")

    prev_help = parser.print_help
    def help_hook(*args, **kwargs):
        sys.stdout.write(yaptex_motd)
        prev_help(*args, **kwargs)
    parser.print_help = help_hook

    args = parser.parse_args()

    print("░▀▄▀▒▄▀▄▒█▀▄░▀█▀▒██▀░▀▄▀ ™")
    print("░▒█▒░█▀█░█▀▒░▒█▒░█▄▄░█▒█")

    assert os.path.isfile(args.input)
    os.makedirs(args.output, exist_ok=True)
    #assert args.target in ["md", "html", "pdf"]

    builder = BuildEngine()

    build_dir = os.path.join(args.output, "raw")
    os.makedirs(build_dir, exist_ok=True)

    log_info("building...")
    try:
        raw_file = builder.build(args.input, build_dir, defines=args.D)
    except:
        log_error("build failed")
        raise

    renderers = {
        "md": MdRenderer,
        "html": HtmlRenderer,
        "pdf": PdfRenderer,
    }

    if (args.target != "raw"):
        def render_dependencies(renderer: Renderer, file: str):
            if renderer.depends_on:
                file = render_dependencies(renderer.depends_on(), file)
            log_info(f"renderer '{renderer.identifier}'")
            render_output = os.path.join(args.output, renderer.identifier)
            os.makedirs(render_output, exist_ok=True)
            return renderer.render(file, render_output)
        
        renderer = renderers[args.target]()

        log_info("rendering...")
        try:
            render_dependencies(renderer, raw_file)
        except:
            log_error("rendering failed")
            raise

    log_info("done")
    
if __name__ == "__main__":
    main()
