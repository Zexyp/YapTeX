import re

ESCAPE_CHAR: str = '\\'
DIRECTIVE_CHAR: str = '#'
MACRO_CHAR: str = '§'
MACRO_ARG_SEPARATOR: str = ','
MACRO_LINE_CONTINUE = ESCAPE_CHAR
VARIABLE_CHAR: str = '%'
QUOTE_CHAR: str = '\"'
DIRECTIVE_ESCAPE_CHAR: str = '#'

REGEX_IDENTIFIER: str = r'[a-zA-Z_][a-zA-Z0-9_]*'
REGEX_NUMBER: str = r'-?\d+'
REGEX_MACRO_LINE_CONTINUE: str = re.escape(MACRO_LINE_CONTINUE)
REGEX_MACRO_CHAR: str = re.escape(MACRO_CHAR)
REGEX_DIRECTIVE_CHAR: str = re.escape(DIRECTIVE_CHAR)
REGEX_VARIABLE_CHAR: str = re.escape(VARIABLE_CHAR)
REGEX_GROUP_QUOTED: str = re.escape(QUOTE_CHAR) + r'((?:' + re.escape(ESCAPE_CHAR) + r'.|[^' + re.escape(QUOTE_CHAR) + re.escape(ESCAPE_CHAR) + r'])*)' + re.escape(QUOTE_CHAR)

def str_escape(value: str) -> str:
    return value.replace("\"", f"{ESCAPE_CHAR}\"")

def str_unescape(value: str) -> str:
    return value.replace(f"{ESCAPE_CHAR}\"", "\"")
