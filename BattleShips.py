from enum import Enum

class FIELD_STATE(Enum):
    EMPTY = "O"
    SHIP_ALIVE = "[]"
    SHIP_HIT = "X"
    MISS = "M"

class Field:
    state = "empty"

    def __init__(self,):
        self.state = FIELD_STATE.EMPTY

    def change_field_state(self, state: FIELD_STATE):
        self.state = state

    def print_field(self):
        return self.state.value


class Board:
    def __init__(self, size: int):
        self.size = size
        self.board = self.create_board()

    def create_board(self):
        return tuple([tuple([Field() for column in range(self.size)]) for row in range(self.size)])

    def print_board(self):
        for row in self.board:
            for field in row:
                print("{} ".format(field.print_field()), end='')
            print()

    def set_ship(self):
        pass
    
class Ship_Type(Enum):
    SMALL = 2
    MEDIUM = 3
    BIG = 4
        
class Ship:
    
    def __init__(self, ship_type: Ship_Type):
        self.occupied_fields = []
        self.size = ship_type.value

    def is_ship_alive(self):
        pass

class Player:

    def __init__(self):
        pass

    def still_has_ships(self):
        pass


class Ship1:
    def __init__(self, size: int, board: Board):
        self.occupied_fields = []
        self.size = size
        self.board = board
        self.in_water = False

    def set_ship(self, pos: tuple, horizontal: bool):
        for i in range(self.size - 1):
            if horizontal:
                if self.board[pos[0] + 1][pos[1]].occupied:
                    self.occupied_fields = []
                    return
                self.occupied_fields.append(self.board[pos[0] + 1][pos[1]])
            else:
                if self.board[pos[0] + 1][pos[1]].occupied:
                    self.occupied_fields = []
                    return
                self.occupied_fields.append(self.board[pos[0]][pos[1] + 1])
        for field in self.occupied_fields:
            field.occupied = True
        self.in_water = True
        return self



class Game:

    def __init__(self):
        self.board1 = Board(10)

    def print_board(self):
        self.board1.print_board()
