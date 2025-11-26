"""renderer for pdf"""

import os
import platform

from xhtml2pdf import pisa
from xhtml2pdf.tags import pisaTagPDFTOC

from ..errors import YapTeXError
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
    def render(self, file: str, output_dir: str, rargs: dict[str, str] = {}):
        pdf_file = os.path.join(output_dir, "index.pdf")
        with open(pdf_file, mode="wb") as pdf, open(file, mode="r", encoding=HTML_ENCODING) as html_file:
            workdir = os.path.dirname(file)

            def link_callback(uri, rel):
                if uri.startswith("data:"):
                    return None
                if os.path.isabs(uri):
                    return None

                log_debug(f"resolving '{uri}'")
                return os.path.join(workdir, uri)

            pisa_status = pisa.CreatePDF(html_file.read(), dest=pdf, link_callback=link_callback)

        if pisa_status.err:
            raise YapTeXError("pisa error")

        return pdf_file
