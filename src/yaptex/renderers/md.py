"""renderer for md"""

import os
import shutil

from . import Renderer

class MdRenderer(Renderer):
    """renderer for md"""

    identifier = "md"

    # post processing options
    def render(self, file: str, output_dir: str):
        # TODO: strip style
        # TODO: colorful headers
        dest = os.path.join(output_dir, "index.md")
        # FIXME
        print("laziness")
        shutil.copytree(os.path.dirname(file), output_dir, dirs_exist_ok=True)
        shutil.copy(file, dest)
        return dest
