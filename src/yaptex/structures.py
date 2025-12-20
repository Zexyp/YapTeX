"""Contains dataclass structures"""

from dataclasses import dataclass
from typing import Callable

@dataclass
class Macro:
    """Representation of macro"""

    params: list[str] = None
    body: str = None
    action: Callable[[list[str], 'BuildEngine'], str] = None
    file: str = NotImplementedError
