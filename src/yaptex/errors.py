"""what is that? is the wind raising the exceptions? act fast! you gotta catch them all"""

class YapTeXError(Exception):
    """uh oh"""

class BuildError(YapTeXError):
    """user error"""

class MalformedError(BuildError):
    """regex spaghetti not suffiecently satisfied"""

class BuildFileNotFoundError(BuildError, FileNotFoundError):
    """was it you or the app that got lost?"""

class RenderingError(YapTeXError):
    """spaghetti failed"""

YapError = YapTeXError
