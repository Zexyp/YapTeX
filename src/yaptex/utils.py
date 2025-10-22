import re

ESCAPE_CHAR: str = '\\'
DIRECTIVE_CHAR: str = '#'
VARIABLE_CHAR: str = '%'
VARIABLE_FORMAT_SEPARATOR: str = ':'
QUOTE_CHAR: str = '\"'
MACRO_CHAR: str = '?'
MACRO_ARG_SEPARATOR: str = ';'
MACRO_LINE_CONTINUE = ESCAPE_CHAR
DECIMAL_SEPARATOR: str = '.'
PAGE_HEADER_SEPARATOR = "---"

REGEX_IDENTIFIER: str = r'[a-zA-Z_][a-zA-Z0-9_]*'
REGEX_NUMBER_INT: str = r'[-+]?\d+'
REGEX_NUMBER_FLOAT: str = rf'[-+]?(?:\d*\{re.escape(DECIMAL_SEPARATOR)}?\d+)'
REGEX_MACRO_LINE_CONTINUE: str = re.escape(MACRO_LINE_CONTINUE)
REGEX_MACRO_CHAR: str = re.escape(MACRO_CHAR)
REGEX_DIRECTIVE_CHAR: str = re.escape(DIRECTIVE_CHAR)
REGEX_VARIABLE_CHAR: str = re.escape(VARIABLE_CHAR)
REGEX_QUOTED: str = re.escape(QUOTE_CHAR) + r'((?:' + re.escape(ESCAPE_CHAR) + r'.|[^' + re.escape(QUOTE_CHAR) + re.escape(ESCAPE_CHAR) + r'])*)' + re.escape(QUOTE_CHAR)
REGEX_MACRO_ARG_SEPARATOR: str = re.escape(MACRO_ARG_SEPARATOR)
REGEX_ESCAPE_CHAR = re.escape(ESCAPE_CHAR)

def str_escape(value: str) -> str:
    return value.replace("\"", f"{ESCAPE_CHAR}\"")

def str_unescape(value: str) -> str:
    return value.replace(f"{ESCAPE_CHAR}\"", "\"")

# remove one of the prefixes
def remove_one_of_prefixes(value, prefixes):
    for prefix in sorted(prefixes, reverse=True):
        if value.startswith(prefix):
            return value.removeprefix(prefix)

# remove one of the prefixes
def remove_one_of_suffixes(value, suffixes):
    for suffix in sorted(suffixes):
        if value.suffix(suffix):
            return value.removesuffix(suffix)