from dataclasses import dataclass
from typing import Callable


@dataclass
class MenuCommand:
    name: str
    command: Callable
    positional_args: tuple[any]
    keyword_args: dict[any, any]
