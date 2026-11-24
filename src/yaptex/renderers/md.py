"""renderer for md"""

import os
import io
import shutil
import re
import base64
import uuid
import mimetypes
import html
from html.parser import HTMLParser
from pprint import pprint
from dataclasses import dataclass
from abc import ABC, abstractmethod

from markdown_it import MarkdownIt

from . import Renderer, RendererConfig, _WritingParser
from .. import utils
from ..log import log_debug

_ASSETS_DIR = "assets"

@dataclass
class MdRendererConfig(RendererConfig):
    flavor: str = None

class _MdImageParser(_WritingParser):
    def process_image(self, url: str, alt: str, id: str) -> str:
        return url

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            dattrs = dict(attrs)
            attrs = [
                (k, self.process_image(dattrs["src"], dattrs.get("alt"), dattrs.get("id")) if k == "src" else v)
                for k, v in attrs
            ]

        super().handle_starttag(tag, attrs)

    def handle_data(self, data):
        def replacor(m):
            url = m.group(1)
            alt = m.group(2)

            if not url.startswith("data:"):
                return m.group(0)
            
            path = self.process_image(url, alt, None)
            return f"![{path}]({alt})"
        
        out_data = re.sub(r'!\[([^\]]*)\]\(([^\)]*)\)', replacor, data)

        super().handle_data(out_data)

class _ExtractingMdImageParser(_MdImageParser):
    def __init__(self, source_dir: str, destination_dir: str, output = None):
        super().__init__(output=output)
        self.destination_dir = destination_dir
        self.source_dir = source_dir

    def process_image(self, url, alt, id):
        assert not os.path.isabs(url)
        if url.startswith("data:"):
            return url
        log_debug("image path: " + url)

        # keep relative path strategy
        file_dst = os.path.join(self.destination_dir, url)
        assert utils.is_file_of_dir(file_dst, self.destination_dir)

        file_src = os.path.join(self.source_dir, url)
        assert os.path.isfile(file_src)

        log_debug(f"from '{file_src}' to '{file_dst}'")
        os.makedirs(os.path.dirname(file_dst), exist_ok=True)
        shutil.copy(file_src, file_dst)

        return url

class _DataExtractingMdImageParser(_MdImageParser):
    def __init__(self, destination_dir: str, relative_to_dir: str, output = None):
        super().__init__(output=output)
        self.destination_dir = destination_dir
        self.relative_to_dir = relative_to_dir

        # deterministic naming
        self.occupied_paths = set()

    def process_image(self, url, alt, id):
        assert not os.path.isabs(url)
        if not url.startswith("data:"):
            return url
        log_debug("image data: " + url)
        
        m = re.match(r"^data:(?P<mime>[^;]+);base64,(?P<data>.+)$", url)
        assert m
        mime = m.group("mime")
        data = m.group("data")
        
        ext = mimetypes.guess_extension(mime) or ".bin"
        raw = base64.b64decode(data)

        nameby = alt or id or "image"
        assert nameby
        basename = utils.slugify(nameby or str(uuid.uuid4()))
        path = os.path.join(self.destination_dir, f"{basename}{ext}")
        
        os.makedirs(self.destination_dir, exist_ok=True)
        i = 1
        while os.path.relpath(path, self.relative_to_dir) in self.occupied_paths:
            path = os.path.join(self.destination_dir, f"{basename}{i}{ext}")
            i += 1

        log_debug(f"writing '{path}'")
        with open(path, "wb") as f:
            f.write(raw)
        
        rp = os.path.relpath(path, self.relative_to_dir)
        self.occupied_paths.add(rp)
        return rp

class _StyleExtractingParser(_WritingParser):
    def __init__(self, output=None):
        super().__init__(output=output)
        self.in_style = False
        self.css = ""

    def handle_starttag(self, tag, attrs):
        if tag == "style":
            assert not self.in_style, "fuck"
            self.in_style = True
            return

        super().handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self.in_style:
            self.css + data
            return
        
        super().handle_data(data)

    def handle_endtag(self, tag):
        if tag == "style":
            assert self.in_style, "fuck"
            self.in_style = False
            return

        super().handle_endtag(tag)

class _YeetusDataExtractingMdImageParser(HTMLParser):
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

        attr_str = " ".join(f'{k}="{html.escape(v)}"' for k, v in attrs)
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

    @staticmethod
    def parse_config(data) -> RendererConfig:
        cfg = MdRendererConfig()
        cfg.flavor = data.get("flavor") or data.get("dialect") or data.get("variant")

        # normalize
        cfg.flavor = "github" if cfg.flavor == "markdown_github" else cfg.flavor

        if cfg.flavor:
            assert "+" not in cfg.flavor, "feature flags not currently supported"
            assert cfg.flavor in ["gh", "github", "none"], "unsupported"

        return cfg

    def _flavor_gh(self, file, dest, output_dir):
        with open(file, mode="r") as fin, open(dest, mode="w") as fout:
            """
            parser = _EmbededImageExtractingParser(fout,
                                                extract_dir=os.path.join(output_dir, _ASSETS_DIR),
                                                relative_to=output_dir)
            """
            parser_style = _StyleExtractingParser(output=fout)
            parser_images_data = _DataExtractingMdImageParser(destination_dir=os.path.join(output_dir, _ASSETS_DIR), relative_to_dir=output_dir, output=parser_style)

            # stream in
            for line in fin:
                parser_images_data.feed(line)
            
            parser_images_data.close()
            parser_style.close
            r"""
            rules = re.findall(r"([^{}]+)\{([^{}]*)\}", parser.css)

            for selector, body in rules:
                declarations = {}
                for item in body.strip().strip(";").split(";"):
                    if ":" in item:
                        property_name, value = item.strip().split(":", 1)
                        declarations[property_name.strip()] = value.strip()
                pprint(declarations)

            fout.seek(0)

            md = MarkdownIt("gfm-like")
            tokens = md.parse(fout.read())

            def walk(tokens):
                for token in tokens:
                    if token.tag:
                        print(token.type, token.tag, token.attrs)
                    if token.children:
                        walk(token.children)

            walk(tokens)
            """

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

        parser_images = _ExtractingMdImageParser(src_dir, output_dir)
        with open(file, mode="r") as f:
            for l in f:
                parser_images.feed(l)
            parser_images.close()
        
        match flavor:
            case "none":
                shutil.copy(file, dest)
            case "gh" | "github":
                self._flavor_gh(file, dest, output_dir)
            case _:
                assert False, "unknown flavvor"
        return dest
