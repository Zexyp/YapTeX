"""download google fonts as resources"""

import os
import re
from .log import log_error, log_info, log_debug

try:
    import requests
except ImportError:
    requests = None
    log_error("requests missing")

from . import PATH_DIR_RESOURCE

HOST = "https://fonts.googleapis.com/"
GET_CSS = HOST + "css?family={family}:bold,italic,bolditalic,normal"

def download(family: str):
    """download font by family name"""
    response = requests.get(GET_CSS.format(family=family), timeout=None)
    assert response.status_code == 200

    font_dir = os.path.join(PATH_DIR_RESOURCE, "font", family)
    os.makedirs(font_dir, exist_ok=True)
    def replacor(m):
        url = m.group(2)
        bn = os.path.basename(url)
        log_debug(f"downloadding '{url}'")
        font_response = requests.get(url, timeout=None)
        with open(os.path.join(font_dir, bn), mode="wb") as file:
            file.write(font_response.content)

        return m.group(1) + bn + m.group(3)

    css = re.sub(r"(src:\surl\()([^)]*)(\))", replacor, response.text)
    with open(os.path.join(font_dir, "style.css"), mode="w") as file:
        file.write(css)
    
    log_info("font downloaded")
