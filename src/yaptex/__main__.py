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

    parser.add_argument("input")
    parser.add_argument("--output", default="./out")
    parser.add_argument("--target", choices=["md", "html", "pdf"], default="raw")
    
    prev_help = parser.print_help;
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
    log_info("building...")
    build_dir = os.path.join(args.output, "raw")
    os.makedirs(build_dir, exist_ok=True)
    raw_file = builder.build(args.input, build_dir)

    renderers = {
        "md": MdRenderer,
        "html": HtmlRenderer,
        "pdf": PdfRenderer,
    }

    if (args.target != "raw"):
        def render_dependencies(renderer: Renderer, file: str):
            if renderer.depends_on:
                file = render_dependencies(renderer.depends_on(), file)
            log_info(f"rendering '{renderer.identifier}'")
            render_output = os.path.join(args.output, renderer.identifier)
            os.makedirs(render_output, exist_ok=True)
            return renderer.render(file, render_output)
        renderer = renderers[args.target]()
        render_dependencies(renderer, raw_file)

    #log_info("rendering...")
    #render(os.path.join(args.output, "index.md"), build_dir)

    log_info("done")
    
if __name__ == "__main__":
    main()
