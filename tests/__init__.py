import os
import unittest

import colorama

# cursed
# some test work with paths, u know
RESOURCE_DIR = os.path.join(os.path.dirname(__file__).removeprefix(os.getcwd()).strip("/\\"), 'resources')

_wrapped_run = unittest.TextTestRunner.run
def _run_wrapper(*args, **kwargs):
    result = _wrapped_run(*args, **kwargs)
    if not colorama:
        return result

    if result.wasSuccessful():
        print(colorama.Fore.GREEN + "yippee" + colorama.Fore.RESET)
    else:
        print(colorama.Fore.RED + "fuck" + colorama.Fore.RESET)
    return result

unittest.TextTestRunner.run = _run_wrapper
