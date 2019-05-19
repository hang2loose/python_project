class Field:
    occupied = False
    state = "empty"


class Board:
    def __init__(self, size: int):
        self.size = size

    def create_board(self):
        return tuple([tuple([Field() for column in range(self.size)]) for row in range(self.size)])

    def draw_board(self):
        pass
