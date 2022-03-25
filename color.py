
class Color:
    def __init__(self, r: float, g: float, b: float):
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
    """
        @property
        def rgb(self):
            return constrain(self._r), constrain(self._g), constrain(self._b)
    
        @property
        def invert_rgb(self):
            return constrain(-self._r), constrain(-self._g), constrain(-self._b)
    
        @property
        def gbr(self):
            return constrain(self._g), constrain(self._b), constrain(self._r)
    
        @property
        def invert_gbr(self):
            return constrain(-self._g), constrain(-self._b), constrain(-self._r)
    
        @property
        def brg(self):
            return constrain(self._b), constrain(self._r), constrain(self._g)
    
        @property
        def invert_brg(self):
            return constrain(-self._b), constrain(-self._r), constrain(-self._g)
    """

def constrain(c):
    result = c * 255
    result %= 255
    while result < 0:
        result + 255
    return int(result)
