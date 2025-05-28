import colorama

colorama.init()

def log_debug(msg):
    print(f"{colorama.Fore.LIGHTBLACK_EX}b: {msg}{colorama.Fore.RESET}")

def log_directive(msg):
    print(f"{colorama.Fore.CYAN}d: {msg}{colorama.Fore.RESET}")

def log_info(msg):
    print(f"i: {msg}")

def log_error(msg):
    print(f"{colorama.Fore.RED}e: {msg}{colorama.Fore.RESET}")

def log_warning(msg):
    print(f"{colorama.Fore.YELLOW}w: {msg}{colorama.Fore.RESET}")