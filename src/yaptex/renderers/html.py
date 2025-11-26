"""renderer for html"""

import os
import shutil

import pygments
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.formatters import HtmlFormatter
from markdown_it import MarkdownIt

from ..log import log_debug, log_warning
from . import Renderer
from .. import PATH_DIR_RESOURCE
from .. import fonts

HTML_ENCODING = "utf8"

class HtmlRenderer(Renderer):
    """renderer for html"""

    identifier = "html"

    # html does not need post processing
    def render(self, file: str, output_dir: str, rargs: dict[str, str] = {}):
        assert os.path.isfile(file)

        styleshim = None
        def highlight(content, lang, attrs) -> str:
            if not lang:
                log_debug("empty lang")
                return None

            nonlocal styleshim

            try:
                lexer = get_lexer_by_name(lang)
            except pygments.util.ClassNotFound:
                try:
                    lexer = get_lexer_for_filename(f"*.{lang}")
                except pygments.util.ClassNotFound:
                    log_warning(f"lexer for '{lang}' not found")
                    return None
            # https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
            #["default", "bw", "sas", "staroffice", "xcode", "monokai", "lightbulb", "github-dark", "rrt"]
            # TODO: make this configurable

            formatter_style = rargs.get("code_style", "default")
            formatter = HtmlFormatter(style=formatter_style)
            if not styleshim:
                styleshim = formatter.get_style_defs(".highlight")

            return pygments.highlight(content, lexer, formatter)

        md = MarkdownIt("commonmark", {"linkify": True})

        md.enable(["linkify", "table"])
        md.options.highlight = highlight
        with open(file, mode='r', encoding="utf8") as source:
            content = md.render(source.read())

        html_file = os.path.join(output_dir, "index.html")

        font_family = rargs.get("font_family", "Bitter")
        # by default xhtml2pdf is useless because it can't even render some basic characters
        shutil.copytree(os.path.join(PATH_DIR_RESOURCE, "font", font_family), os.path.join(output_dir, "font", font_family), dirs_exist_ok=True)

        content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document \\(o_o)/</title>
    <link rel="stylesheet" href="font/{font_family}/style.css">
    <style>
    body {{
        font-family: {font_family};
    }}
{styleshim if styleshim else ""}
    </style>
</head>
<body>
{content}
</body>
</html>
"""

        # copy additional resources
        # this should be recursive one day
        import lxml.html
        import urllib.parse
        tree = lxml.html.fromstring(content)
        def is_url(link):
            parsed = urllib.parse.urlparse(link)
            return bool(parsed.scheme and parsed.netloc)
        referenced_paths = [link for link in tree.xpath('//img[@src]/@src') if not is_url(link)]

        # TODO: decide behaviour (relative, assets)
        # this is keep relative strategy
        for path in referenced_paths:
            log_debug(f"referenced path '{path}'")

            if os.path.isabs(path):
                log_warning(f"suppressed absolute path! ('{path}')")
                continue

            ref_rel_path = os.path.join(os.path.dirname(file), path)
            if not os.path.isfile(ref_rel_path):
                log_warning(f"file not found! ('{ref_rel_path}')")
                continue

            dest = os.path.join(output_dir, path)
            if not os.path.abspath(dest).startswith(os.path.abspath(output_dir)):
                log_warning(f"illegal path! ('{path}')")
                continue

            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy(ref_rel_path, dest)

        with open(html_file, mode='w', encoding=HTML_ENCODING) as html:
            html.write(content)
        return html_file
