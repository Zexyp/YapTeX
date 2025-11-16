class YapTeXError(Exception):
    pass

YapError = YapTeXError

class BuildError(YapTeXError):
    pass

class MalformedError(BuildError):
    pass

class BuildFileNotFoundError(BuildError, FileNotFoundError):
    pass