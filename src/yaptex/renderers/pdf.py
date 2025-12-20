"""renderer for pdf"""

import os
import platform

from xhtml2pdf import pisa
from xhtml2pdf.tags import pisaTagPDFTOC

from ..errors import RenderingError
from ..log import log_debug
from . import Renderer
from .html import HtmlRenderer, HTML_ENCODING

# ! monkey patch !
if platform.system() == "Windows":
    log_debug("monkey patching")
    from xhtml2pdf.files import pisaFileObject
    pisaFileObject.getNamedFile = lambda self: self.uri

class PdfRenderer(Renderer):
    """renderer for pdf"""

    identifier = "pdf"
    depends_on = HtmlRenderer

    # this needs preparation
    def render(self, filepath: str, output_dir: str, rargs: dict[str, str] = {}):
        pdf_filepath = os.path.join(output_dir, "index.pdf")
        with open(pdf_filepath, mode="wb") as pdf_file, open(filepath, mode="r", encoding=HTML_ENCODING) as html_file:
            filedir = os.path.dirname(filepath)

            def link_callback(uri, basepath):
                if uri.startswith("data:"):
                    raise NotImplementedError
                if os.path.isabs(uri):
                    raise NotImplementedError

                log_debug(f"resolving '{uri}' ('{basepath}')")

                def dir_of_file(path):
                    # macos platform fuckery
                    if os.path.isdir(path):
                        return path
                    return os.path.dirname(path)
                
                if os.path.isabs(basepath):
                    result = os.path.join(dir_of_file(basepath), uri)
                else:
                    result = os.path.join(dir_of_file(os.path.join(filedir, basepath)), uri)
                                
                log_debug(f"resulting '{result}'")
                return result

            pisa_status = pisa.CreatePDF(html_file.read(), path=filepath, dest=pdf_file, link_callback=link_callback, encoding=HTML_ENCODING)

        if pisa_status.err:
            raise RenderingError("pisa error")

        return pdf_file
