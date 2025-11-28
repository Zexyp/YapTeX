"""simmple logging proxy"""

import sys

col_debug = ""
col_directive = ""
col_error = ""
col_warning = ""
col_reset = ""

def log_print(msg):
    """hate docstrings"""
    print(msg, file=sys.stdout)

def log_debug(msg):
    """hate docstrings"""
    print(f"{col_debug}b: {msg}{col_reset}", file=sys.stdout)

def log_directive(msg):
    """hate docstrings"""
    print(f"{col_directive}d: {msg}{col_reset}", file=sys.stdout)

def log_info(msg):
    """hate docstrings"""
    print(f"i: {msg}", file=sys.stdout)

def log_error(msg):
    """hate docstrings"""
    print(f"{col_error}e: {msg}{col_reset}", file=sys.stderr)

def log_warning(msg):
    """hate docstrings"""
    print(f"{col_warning}w: {msg}{col_reset}", file=sys.stderr)

try:
    import colorama

    colorama.init()

    col_debug = colorama.Fore.LIGHTBLACK_EX
    col_directive = colorama.Fore.CYAN
    col_error = colorama.Fore.RED
    col_warning = colorama.Fore.YELLOW
    col_reset = colorama.Fore.RESET
except ImportError as e:
    log_warning(f"no coloring ({e})")
