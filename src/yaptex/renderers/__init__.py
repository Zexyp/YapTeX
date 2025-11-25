"""builtin renderers"""

from abc import ABC, abstractmethod

from ..log import log_error

# TODO: add flavoring

class Renderer(ABC):
    """base for renderers"""
    depends_on = None
    identifier = None

    @abstractmethod
    def render(self, file: str, output_dir: str):
        """render stuff"""

try:
    from .md import MdRenderer
except ImportError as e:
    log_error(f"failed to import renderer: {e}")
try:
    from .html import HtmlRenderer
except ImportError as e:
    log_error(f"failed to import renderer: {e}")
try:
    from .pdf import PdfRenderer
except ImportError as e:
    log_error(f"failed to import renderer: {e}")
