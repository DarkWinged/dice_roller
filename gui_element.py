from abc import abstractmethod, ABC

import tcod


class GuiElement(ABC):
    @property
    @abstractmethod
    def activated(self) -> bool: pass

    @abstractmethod
    def activate(self): pass

    @abstractmethod
    def deactivate(self): pass

    @property
    @abstractmethod
    def paused(self) -> bool: pass

    @abstractmethod
    def pause(self): pass

    @abstractmethod
    def unpause(self): pass

    @property
    @abstractmethod
    def position(self) -> tuple[int, int]: pass

    @position.setter
    @abstractmethod
    def position(self, new_pos: tuple[int, int]): pass

    @property
    @abstractmethod
    def height(self) -> int: pass

    @height.setter
    @abstractmethod
    def height(self, new_height: int): pass

    @property
    @abstractmethod
    def width(self) -> int: pass

    @property
    @abstractmethod
    def canvas(self) -> tcod.Console: pass

    @canvas.setter
    @abstractmethod
    def canvas(self, console: tcod.Console): pass

    @width.setter
    @abstractmethod
    def width(self, new_width: int): pass

    @abstractmethod
    def render(self): pass
