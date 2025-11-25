"""simmple logging proxy"""

import sys

import colorama

colorama.init()

def log_print(msg):
    """hate docstrings"""
    print(msg, file=sys.stdout)

def log_debug(msg):
    """hate docstrings"""
    print(f"{colorama.Fore.LIGHTBLACK_EX}b: {msg}{colorama.Fore.RESET}", file=sys.stdout)

def log_directive(msg):
    """hate docstrings"""
    print(f"{colorama.Fore.CYAN}d: {msg}{colorama.Fore.RESET}", file=sys.stdout)

def log_info(msg):
    """hate docstrings"""
    print(f"i: {msg}", file=sys.stdout)

def log_error(msg):
    """hate docstrings"""
    print(f"{colorama.Fore.RED}e: {msg}{colorama.Fore.RESET}", file=sys.stderr)

def log_warning(msg):
    """hate docstrings"""
    print(f"{colorama.Fore.YELLOW}w: {msg}{colorama.Fore.RESET}", file=sys.stderr)
