"""what is that? is the wind raising the exceptions? act fast! you gotta catch them all"""

class YapTeXError(Exception):
    """uh oh"""

YapError = YapTeXError

class BuildError(YapTeXError):
    """user error"""

class MalformedError(BuildError):
    """regex spaghetti not suffiecently satisfied"""

class BuildFileNotFoundError(BuildError, FileNotFoundError):
    """did the app or you got lost?"""
