from enum import Enum

class FIELD_STATE(Enum):
    EMPTY = "O"
    SHIP_ALIVE = "[]"
    SHIP_HIT = "X"
    MISS = "M"


class Ship_Type(Enum):
    SMALL = 2
    MEDIUM = 3
    BIG = 4


class SHIP_ORIENTATION(Enum):
    HORIZONTAL = "h"
    VERTIKAL = "v"