"""
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
import re
from abc import ABC, abstractmethod
from io import TextIOWrapper, StringIO
from typing import Generator
import sys
from datetime import datetime
import argparse

import colorama

from engine import BuildEngine
from renderers import *
from log import *

def render(source_file, dir_output):

    ###

    PATH_DIR_RESOURCE = os.path.join(os.path.dirname(__file__), "res")
    assert os.path.isdir(PATH_DIR_RESOURCE)

    assert os.path.isfile(source_file)

    from markdown_it import MarkdownIt
    import shutil

    styleshim = None
    def highlight(content, lang, attrs) -> str:
        if not lang:
            log_debug("empty lang")
            return

        nonlocal styleshim

        import pygments
        from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
        from pygments.formatters import HtmlFormatter

        try:
            lexer = get_lexer_by_name(lang)
        except pygments.util.ClassNotFound:
            try:
                lexer = get_lexer_for_filename(f"*.{lang}")
            except pygments.util.ClassNotFound:
                log_warning(f"lexer for '{lang}' not found")
                return
        
        formatter = HtmlFormatter(style='bw');
        if not styleshim:
            styleshim = formatter.get_style_defs(".highlight")
        
        return pygments.highlight(content, lexer, formatter)

    md = MarkdownIt("commonmark", {"linkify": True})
    md.enable(["linkify"])
    md.options.highlight = highlight
    with open(source_file, mode='r', encoding="utf8") as source:
        content = md.render(source.read())

    html_file = os.path.join(dir_output, "build.html")

    # by default xhtml2pdf is useless because it can't even render some basic characters
    shutil.copytree(os.path.join(PATH_DIR_RESOURCE, "font"), os.path.join(dir_output, "font"), dirs_exist_ok=True)

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document \\(o_o)/</title>
    <style>
    @font-face {{
        font-family: Bitter;
        src: url("font/Bitter/Bitter-Regular.ttf");
    }}
    @font-face {{
        font-family: Bitter;
        src: url("font/Bitter/Bitter-Bold.ttf");
        font-weight: bold;
    }}
    @font-face {{
        font-family: Bitter;
        src: url("font/Bitter/Bitter-Italic.ttf");
        font-style: italic;
    }}
    @font-face {{
        font-family: Bitter;
        src: url("font/Bitter/Bitter-{print('sussy patch') or 'Regular'}.ttf");
        font-weight: bold;
        font-style: italic;
    }}

    body {{
        font-family: Bitter;
    }}
{styleshim if styleshim else ""}
    </style>
</head>
<body>
{content}
</body>
</html>
"""
    
    with open(html_file, mode='w', encoding="utf8") as html:
        html.write(content)

    ###

    from xhtml2pdf import pisa
    from xhtml2pdf.tags import pisaTagPDFTOC
    # ! monkey patch !
    import platform
    if platform.system() == "Windows":
        log_debug("monkey patching")
        from xhtml2pdf.files import pisaFileObject
        pisaFileObject.getNamedFile = lambda self: self.uri

    with open(os.path.join(dir_output, "build.pdf"), mode="wb") as pdf:
        workdir = os.path.dirname(html_file)

        def link_callback(uri, rel):
            if uri.startswith("data:"):
                return
            if os.path.isabs(uri):
                return
            
            log_debug(f"resolving '{uri}'")
            return os.path.join(workdir, uri)
        
        pisa_status = pisa.CreatePDF(content, dest=pdf, link_callback=link_callback)

    if pisa_status.err:
        raise Exception("pisa error")

def main():
    print("░▀▄▀▒▄▀▄▒█▀▄░▀█▀▒██▀░▀▄▀ ™")
    print("░▒█▒░█▀█░█▀▒░▒█▒░█▄▄░█▒█")

    parser = argparse.ArgumentParser()

    parser.add_argument("input")
    parser.add_argument("--output", default="./out")
    parser.add_argument("--target", choices=["md", "html", "pdf"], default="raw")

    args = parser.parse_args()

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
