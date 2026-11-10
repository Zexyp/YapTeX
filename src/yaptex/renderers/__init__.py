"""builtin renderers"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..log import log_error, log_debug, log_error, log_warning, log_info

# TODO: add flavoring

@dataclass
class RendererConfig(ABC):
    """rargs definition"""
    pass

class Renderer(ABC):
    """base for renderers"""
    depends_on = None
    identifier = None

    @staticmethod
    @abstractmethod
    def parse_config(data) -> RendererConfig:
        pass

    @abstractmethod
    def render(self, file: str, output_dir: str, rargs: dict[str, str]):
        """render stuff"""
        pass

    def log_debug(self, msg: str):
        """engine log"""
        log_debug(f"[{self.identifier}] {msg}")

    def log_info(self, msg: str):
        """engine log"""
        log_info(f"[{self.identifier}] {msg}")
    
    def log_error(self, msg: str):
        """engine log"""
        log_error(f"[{self.identifier}] {msg}")

    def log_warning(self, msg: str):
        """engine log"""
        log_warning(f"[{self.identifier}] {msg}")

try:
    from .md import MdRenderer
except ImportError as e:
    log_error(f"failed to import renderer: {e}")
    MdRenderer = None
try:
    from .html import HtmlRenderer
except ImportError as e:
    log_error(f"failed to import renderer: {e}")
    HtmlRenderer = None
try:
    from .pdf import PdfRenderer
except ImportError as e:
    log_error(f"failed to import renderer: {e}")
    PdfRenderer = None
