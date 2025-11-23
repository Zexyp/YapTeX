"""we need to init some stuff here"""
from .renderers import *

renderer_types = {}

def add_renderer_type(rend: type[Renderer]):
    """syncronizes identiefier in renderer_types dict"""
    assert rend.identifier not in renderer_types
    renderer_types[rend.identifier] = rend

add_renderer_type(MdRenderer)
add_renderer_type(HtmlRenderer)
add_renderer_type(PdfRenderer)
