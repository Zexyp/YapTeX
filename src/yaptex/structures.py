from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class Macro:
    params: list[str] = None
    body: str = None
    action: Callable[[list[str], 'BuildEngine'], Any] = None
    file: str = None # just for the lols
