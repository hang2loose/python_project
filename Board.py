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


class Ship:
    def __init__(self, size: int, pos: int, horizontal: bool, board: tuple):
        self.occupied_fields = None
        self.size = size
        self.board = board
        self.horizontal = horizontal
        self.pos = pos

    def set_ship(self, size: int):
        for i in range(size - 1):
            if self.horizontal:
                if self.board[self.pos + 1][self.pos].occupied:
                    self.occupied_fields = None
                    return
                self.occupied_fields.append(self.board[self.pos + 1][self.pos])
            else:
                if self.board[self.pos + 1][self.pos].occupied:
                    self.occupied_fields = None
                    return
                self.occupied_fields.append(self.board[self.pos][self.pos + 1])
        for field in self.occupied_fields:
            field.occupied = True
