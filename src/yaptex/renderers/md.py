"""renderer for md"""

import os
import shutil
import re
import base64
import uuid
import mimetypes
from html.parser import HTMLParser

from . import Renderer
from .. import utils

_ASSETS_DIR = "assets"

class _GitHubMdConvertingParser(HTMLParser):
    def __init__(self, out_file, extract_dir, relative_to):
        super().__init__()
        self.out = out_file
        self.extract_dir: str = extract_dir
        self.relative_to: str = relative_to
        self.in_style = False
        self.occupied_paths = set()
        self.css = ""

    def dump_image(self, url, nameby) -> str:
        m = re.match(r"^data:(?P<mime>[^;]+);base64,(?P<data>.+)$", url)
        assert m
        mime = m.group("mime")
        data = m.group("data")
        
        ext = mimetypes.guess_extension(mime) or ".bin"
        raw = base64.b64decode(data)

        basename = utils.slugify(nameby or str(uuid.uuid4()))
        path = os.path.join(self.extract_dir, f"{basename}{ext}")
        
        os.makedirs(self.extract_dir, exist_ok=True)
        i = 1
        while os.path.relpath(path, self.relative_to) in self.occupied_paths:
            path = os.path.join(self.extract_dir, f"{basename}{i}{ext}")
            i += 1

        self.log_debug(f"writing '{path}'")
        with open(path, "wb") as f:
            f.write(raw)
        
        rp = os.path.relpath(path, self.relative_to)
        self.occupied_paths.add(rp)
        return rp

    def handle_starttag(self, tag, attrs):
        if tag == "style":
            self.in_style = True
            return

        if self.in_style:
            assert False, "fuck"
            return

        if tag == "img":
            dattrs = dict(attrs)
            nameby = dattrs.get("alt") or dattrs.get("id")
            attrs = [
                (k, self.dump_image(v, nameby) if k == "src" and v.startswith("data:") else v)
                for k, v in attrs
            ]

        # TODO: not safe
        attr_str = " ".join(f'{k}="{v}"' for k, v in attrs)
        self.out.write(f"<{tag}{(' ' + attr_str) if attr_str else ''}>")

    def handle_endtag(self, tag):
        if tag == "style":
            raise NotImplementedError("parse css")
            self.in_style = False
            return

        if self.in_style:
            return

        self.out.write(f"</{tag}>")

    def handle_data(self, data):
        if self.in_style:
            self.css + data
            return
        
        # TODO: line by line for headers
        
        def replacor(m):
                url = m.group(1)
                alt = m.group(2)

                if not url.startswith("data:"):
                    return m.group(0)
                
                path = self.dump_image(url, alt)
                return f"![{path}]({alt})"
        
        out_data = re.sub(r'!\[([^\]]*)\]\(([^\)]*)\)', replacor, data)

        for line in out_data.splitlines(keepends=True):
            if m := re.match(r'^(#+) ', line):
                level = len(m.group(1))

        self.out.write(out_data)

class MdRenderer(Renderer):
    """renderer for md"""

    identifier = "md"       

    # post processing options
    def render(self, file: str, output_dir: str, rargs: dict[str, str] = {}):
        # https://gist.github.com/vimtaai/99f8c89e7d3d02a362117284684baa0f
        # https://github.github.com/gfm/
        # https://docs.gitlab.com/user/markdown/
        flavor = rargs.get("flavor") or rargs.get("dialect") or "none"
        self.log_debug(f"flavor: {flavor}")

        dest = os.path.join(output_dir, "index.md")
        # FIXME
        src_dir = os.path.abspath(os.path.dirname(file))
        def ignore_func(dir, files):
            if src_dir != os.path.abspath(dir):
                return set()
            return {"index"} if "index" in files else set()
        
        print("laziness")        
        shutil.copytree(os.path.dirname(file), output_dir, dirs_exist_ok=True, ignore=ignore_func)
        
        match flavor:
            case "none":
                shutil.copy(file, dest)
            case "gh" | "github":
                with open(file, mode="r") as fin, open(dest, mode="w") as fout:
                    parser = _GitHubMdConvertingParser(fout,
                                                      extract_dir=os.path.join(output_dir, _ASSETS_DIR),
                                                      relative_to=output_dir)
                    
                    # stream in
                    for line in fin:
                        parser.feed(line)
                    
                    parser.close()
            case _:
                assert False, "unknown flavvor"
        return dest
