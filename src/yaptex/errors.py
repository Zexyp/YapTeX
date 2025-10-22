class YapError(Exception):
    pass

class BuildError(YapError):
    pass

class MalformedError(BuildError):
    pass
