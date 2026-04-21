"""renderer for md"""

import os
import shutil

from . import Renderer

class MdRenderer(Renderer):
    """renderer for md"""

    identifier = "md"

    # post processing options
    def render(self, file: str, output_dir: str, rargs: dict[str, str] = {}):
        # TODO: strip style
        # TODO: extract base64 images
        # TODO: colorful headers
        # https://gist.github.com/vimtaai/99f8c89e7d3d02a362117284684baa0f
        # https://github.github.com/gfm/
        # https://docs.gitlab.com/user/markdown/
        flavor = rargs.get("flavor", rargs.get("dialect", "none"))
        if flavor != "none":
            raise NotImplementedError("flavor not implemented")

        dest = os.path.join(output_dir, "index.md")
        # FIXME
        print("laziness")
        shutil.copytree(os.path.dirname(file), output_dir, dirs_exist_ok=True)
        shutil.copy(file, dest)
        return dest
