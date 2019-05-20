class Field:
    occupied = False
    state = "empty"


class Board:
    def __init__(self, size: int):
        self.size = size

    def create_board(self):
        return tuple([tuple([Field() for column in range(self.size)]) for row in range(self.size)])


class Ship:
    def __init__(self, size: int, board: tuple):
        self.occupied_fields = []
        self.size = size
        self.board = board

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
        return self


class Player:
    def __init__(self, board: tuple, ships: list):
        self.board = board
        self.ships = ships

    def set_ships(self):
        for ship in self.ships:
            x_pos = int(input("Xpos: "))
            y_pos = int(input("Ypos: "))
            pos = (x_pos, y_pos)
            ship.set_ship(pos, True)

    def shoot(self):
        x_pos = int(input("Xpos: "))
        y_pos = int(input("Ypos: "))
        pos = (x_pos, y_pos)

        if self.board[pos[0]][pos[1]].occupied and self.board[pos[0]][pos[1]].state is "empty":
            self.board[pos[0]][pos[1]].state = "hit"
        else:
            self.board[pos[0]][pos[1]].state = "missed"

    def draw_board(self):
        pass


class Game:
    def __init__(self):
        board_a = Board(10).create_board()
        board_b = Board(10).create_board()

        ships_A = [Ship(2, board_a), Ship(2, board_a), Ship(4, board_a)]
        ships_B = [Ship(2, board_b), Ship(2, board_b), Ship(4, board_b)]

        self.player_A = Player(board_a, ships_A)
        self.player_B = Player(board_b, ships_B)

    def players_set_ship(self):
        self.player_A.set_ships()
        self.player_B.set_ships()

    def play(self):
        self.players_set_ship()
        player_a_turn = True
        while True:
            player_a_turn if self.player_A.shoot() else self.player_B.shoot()
            player_a_turn = not player_a_turn
