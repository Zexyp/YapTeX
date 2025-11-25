"""we need to init some stuff here"""
import os

PATH_DIR_RESOURCE = os.path.join(os.path.dirname(__file__), "res")
assert os.path.isdir(PATH_DIR_RESOURCE)

from .renderers import *

renderer_types = {}

def add_renderer_type(rend: type[Renderer]):
    """syncronizes identiefier in renderer_types dict"""
    assert rend.identifier not in renderer_types
    renderer_types[rend.identifier] = rend

# quite messy hack
if "MdRenderer" in locals(): add_renderer_type(MdRenderer)
if "HtmlRenderer" in locals(): add_renderer_type(HtmlRenderer)
if "PdfRenderer" in locals(): add_renderer_type(PdfRenderer)
