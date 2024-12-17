import re

ESCAPE_CHAR: str = '\\'
PREPROCESSOR_CHAR: str = '#'
MACRO_CHAR: str = "#"
MACRO_ARG_SEPARATOR: str = ";"
QUOTE_CHAR: str = "\""

REGEX_IDENTIFIER: str = r'[a-zA-Z0-9_]+'
REGEX_NUMBER: str = r'-?\d+'
REGEX_MACRO_CHAR: str = re.escape(MACRO_CHAR)
REGEX_PREPROCESSOR_CHAR: str = re.escape(PREPROCESSOR_CHAR)
REGEX_GROUP_IDENTIFIER: str = rf'({REGEX_IDENTIFIER})'
REGEX_GROUP_NUMBER: str = rf'({REGEX_NUMBER})'
REGEX_GROUP_QUOTED: str = re.escape(QUOTE_CHAR) + r'((?:' + re.escape(ESCAPE_CHAR) + r'.|[^' + re.escape(QUOTE_CHAR) + re.escape(ESCAPE_CHAR) + r'])*)' + re.escape(QUOTE_CHAR)

def str_escape(value: str) -> str:
    return value.replace("\"", f"{ESCAPE_CHAR}\"")

def str_unescape(value: str) -> str:
    return value.replace(f"{ESCAPE_CHAR}\"", "\"")
