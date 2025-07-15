from abc import ABC, abstractmethod
import os

from .log import *

HTML_ENCODING = "utf8"

class Renderer(ABC):
    depends_on = None
    identifier = None

    @abstractmethod
    def render(self, file: str, output_dir: str):
        pass

class MdRenderer(Renderer):
    identifier = "md"

    # post processing options
    def render(self, file: str, output_dir: str):
        # TODO: strip style
        dest = os.path.join(output_dir, "index.md")
        import shutil
        print("laziness")
        shutil.copytree(os.path.dirname(file), output_dir, dirs_exist_ok=True)
        shutil.copy(file, dest)
        return dest

class HtmlRenderer(Renderer):
    identifier = "html"

    # html does not need post processing
    def render(self, file: str, output_dir: str):
        PATH_DIR_RESOURCE = os.path.join(os.path.dirname(__file__), "res")
        assert os.path.isdir(PATH_DIR_RESOURCE)

        assert os.path.isfile(file)

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
        md.enable(["linkify", "table"])
        md.options.highlight = highlight
        with open(file, mode='r', encoding="utf8") as source:
            content = md.render(source.read())

        html_file = os.path.join(output_dir, "index.html")

        # by default xhtml2pdf is useless because it can't even render some basic characters
        shutil.copytree(os.path.join(PATH_DIR_RESOURCE, "font"), os.path.join(output_dir, "font"), dirs_exist_ok=True)

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
        
        # copy additional resources
        # this should be recursive one day
        import lxml.html
        import urllib.parse
        tree = lxml.html.fromstring(content)
        def is_url(link):
            parsed = urllib.parse.urlparse(link)
            return bool(parsed.scheme and parsed.netloc)
        referenced_paths = [link for link in tree.xpath('//img[@src]/@src') if not is_url(link)]

        # decide behaviour (relative, assets)
        # this is keep relative strategy
        for path in referenced_paths:
            log_debug(f"referenced path '{path}'")

            if (os.path.isabs(path)):
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

class PdfRenderer(Renderer):
    identifier = "pdf"
    depends_on = HtmlRenderer

    # this needs preparation
    def render(self, file: str, output_dir: str):
        from xhtml2pdf import pisa
        from xhtml2pdf.tags import pisaTagPDFTOC
        # ! monkey patch !
        import platform
        if platform.system() == "Windows":
            log_debug("monkey patching")
            from xhtml2pdf.files import pisaFileObject
            pisaFileObject.getNamedFile = lambda self: self.uri

        pdf_file = os.path.join(output_dir, "index.pdf")
        with open(pdf_file, mode="wb") as pdf, open(file, mode="r", encoding=HTML_ENCODING) as html_file:
            workdir = os.path.dirname(file)

            def link_callback(uri, rel):
                if uri.startswith("data:"):
                    return
                if os.path.isabs(uri):
                    return
                
                log_debug(f"resolving '{uri}'")
                return os.path.join(workdir, uri)
            
            pisa_status = pisa.CreatePDF(html_file.read(), dest=pdf, link_callback=link_callback)

        if pisa_status.err:
            raise Exception("pisa error")

        return pdf_file
