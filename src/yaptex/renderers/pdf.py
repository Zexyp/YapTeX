"""renderer for pdf"""

import os
import platform
import io
from html.parser import HTMLParser

from xhtml2pdf import pisa
from xhtml2pdf.tags import pisaTagPDFTOC

from ..errors import RenderingError
from ..log import log_debug
from . import Renderer, RendererConfig
from .html import HtmlRenderer, HTML_ENCODING

# TODO: converting parser, name is treated as id attribute

# ! monkey patch !
# TODO: add patch for macos
if platform.system() == "Windows":
    log_debug("monkey patching")
    from xhtml2pdf.files import pisaFileObject
    pisaFileObject.getNamedFile = lambda self: self.uri

class _AncorAddingParser(HTMLParser):
    def __init__(self, output):
        super().__init__()
        self.out = output

    def handle_starttag(self, tag, attrs):
        if "id" in (dattrs := dict(attrs)):
            self.out.write(f"<a name=\"{dattrs["id"]}\"></a>")

        # TODO: not safe
        attr_str = " ".join(f'{k}="{v}"' for k, v in attrs)
        self.out.write(f"<{tag}{(' ' + attr_str) if attr_str else ''}>")

    def handle_endtag(self, tag):
        self.out.write(f"</{tag}>")
    
    def handle_data(self, data):
        self.out.write(data)

class PdfRenderer(Renderer):
    """renderer for pdf"""

    @staticmethod
    def parse_config(data) -> RendererConfig:
        raise NotImplementedError

    identifier = "pdf"
    depends_on = HtmlRenderer

    # this needs preparation
    def render(self, filepath: str, output_dir: str, rargs: dict[str, str] = {}):
        pdf_filepath = os.path.join(output_dir, "index.pdf")
        with open(pdf_filepath, mode="wb") as pdf_file, open(filepath, mode="r", encoding=HTML_ENCODING) as html_file:
            filedir = os.path.dirname(filepath)

            def link_callback(uri, basepath):
                if uri.startswith("data:"):
                    return uri
                if os.path.isabs(uri):
                    raise NotImplementedError

                self.log_debug(f"resolving '{uri}' ('{basepath}')")

                def dir_of_file(path):
                    # macos platform fuckery
                    if os.path.isdir(path):
                        return path
                    return os.path.dirname(path)
                
                if os.path.isabs(basepath):
                    result = os.path.join(dir_of_file(basepath), uri)
                else:
                    result = os.path.join(dir_of_file(os.path.join(filedir, basepath)), uri)
                                
                self.log_debug(f"resulting '{result}'")
                return result

            with io.StringIO() as buffer:
                # TODO: stupid, not streaming
                parser = _AncorAddingParser(buffer)
                for line in html_file:
                    parser.feed(line)
                # finally use the buffer
                buffer.seek(0)
                pisa_status = pisa.CreatePDF(buffer.read(), path=filepath, dest=pdf_file, link_callback=link_callback, encoding=HTML_ENCODING)

        if pisa_status.err:
            raise RenderingError("pisa error")

        return pdf_filepath
