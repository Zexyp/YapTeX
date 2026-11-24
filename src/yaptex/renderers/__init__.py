"""builtin renderers"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from html.parser import HTMLParser
import io

from ..log import log_error, log_debug, log_error, log_warning, log_info

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

class _WritingParser(ABC, HTMLParser):
    def __init__(self, output: io.TextIOWrapper | HTMLParser = None):
        super().__init__()
        self.output = output

    def write(self, text: str):
        if self.output is None:
            return
        match self.output:
            case io.TextIOWrapper():
                self.output.write(text)
            case HTMLParser():
                self.output.feed(text)

    def handle_starttag(self, tag, attrs):
        attr_str = " ".join(f'{k}="{html.escape(v)}"' for k, v in attrs)
        self.write(f"<{tag}{(' ' + attr_str) if attr_str else ''}>")

    def handle_endtag(self, tag):
        self.write(f"</{tag}>")

    def handle_data(self, data):
        self.write(data)

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
