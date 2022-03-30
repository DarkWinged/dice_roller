
class Color:
    def __init__(self, r: float, g: float, b: float, /):
        self._r = r
        self._g = g
        self._b = b

    def rgb(self, invert: bool = None, shift: int = None):
        if invert is None:
            invert = False
        if shift is None:
            shift = 0

        r = self._r
        g = self._g
        b = self._b

        if invert:
            r = -r
            g = -g
            b = -b

        match shift % 3:
            case 0:
                return constrain(r), constrain(g), constrain(b)
            case 1:
                return constrain(g), constrain(b), constrain(r)
            case 2:
                return constrain(b), constrain(r), constrain(g)


def constrain(color_val: float, /) -> int:
    color_val = color_val * 255
    color_val %= 255
    while color_val < 0:
        color_val + 255
    return int(color_val)
