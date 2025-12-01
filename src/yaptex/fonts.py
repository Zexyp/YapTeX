"""download google fonts as resources"""

import os
import re
from .log import log_error, log_info, log_debug
import json
from textwrap import dedent

try:
    import requests
except ImportError:
    requests = None
    log_error("requests missing")

from . import PATH_DIR_RESOURCE

HOST = "https://fonts.google.com/"
GET_LIST = HOST + "download/list?family={family}"

def download(family: str):
    """download font by family name"""
    url = GET_LIST.format(family=family)
    log_debug(f"requesting '{url}'")
    # can't have shit when google
    #headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0'}
    response = requests.get(url, timeout=None)
    assert response.status_code == 200, f"was {response.status_code}"

    json_data = json.loads(response.text.removeprefix(")]}'"))
    
    font_dir = os.path.join(PATH_DIR_RESOURCE, "font", family)
    os.makedirs(font_dir, exist_ok=True)
    names = []
    # iterate manifest files
    for el_file in json_data["manifest"]["fileRefs"]:
        filename = el_file["filename"]
        if not filename.endswith(".ttf"): # quick drop
            log_debug(f"skippping '{filename}'")
            continue
        
        font_url = el_file["url"]
        log_debug(f"downloading '{filename}' ({font_url})")
        
        font_response = requests.get(font_url)
        assert font_response.status_code == 200, f"was {font_response.status_code}"

        bn = os.path.basename(filename)
        assert bn not in names
        names.append(bn) # capture filename
        with open(os.path.join(font_dir, bn), mode="wb") as file:
            file.write(font_response.content)

    log_info("building css")

    
    names.sort(key=lambda x: len(x))

    src_regular = next(iter([n for n in names if "regular" in n.lower()]))
    src_bolditalic = next(iter([n for n in names if "bolditalic" in n.lower()])) or src_regular
    src_italic = next(iter([n for n in names if "italic" in n.lower()])) or src_regular
    src_bold = next(iter([n for n in names if "bold" in n.lower()])) or src_regular

    log_debug(f"regular:    '{src_regular}'")
    log_debug(f"italic:     '{src_italic}'")
    log_debug(f"bold:       '{src_bold}'")
    log_debug(f"bolditalic: '{src_bolditalic}'")

    css = f"""
    /* YapTeX generated */
    @font-face {{
        font-family: '{family}';
        font-weight: normal;
        font-style: normal;
        src: url({src_regular});
    }}

    @font-face {{
        font-family: '{family}';
        font-weight: normal;
        font-style: italic;
        src: url({src_italic});
    }}

    @font-face {{
        font-family: '{family}';
        font-weight: bold;
        font-style: normal;
        src: url({src_bold});
    }}

    @font-face {{
        font-family: '{family}';
        font-weight: bold;
        font-style: italic;
        src: url({src_bolditalic});
    }}
    """
    css = dedent(css).lstrip()

    with open(os.path.join(font_dir, "style.css"), mode="w") as file:
        file.write(css)

    log_info("font downloaded")

def installed() -> list[str]:
    fonts_dir = os.path.join(PATH_DIR_RESOURCE, "font")
    return [f for f in os.listdir(fonts_dir) if os.path.isdir(os.path.join(fonts_dir, f))]
