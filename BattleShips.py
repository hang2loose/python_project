from BattleShipsEnums import *


class Field:
    state = "empty"

    def __init__(self, ):
        self.state = FIELD_STATE.EMPTY

    def change_field_state(self, state: FIELD_STATE):
        self.state = state

    def print_field(self):
        return self.state.value

    def get_state(self):
        return self.state


class Ship:

    def __init__(self, ship_type: Ship_Type):
        self.occupied_fields = []
        self.size = ship_type.value
        self.orientation = SHIP_ORIENTATION.HORIZONTAL

    def is_ship_alive(self):
        pass

    def switch_orientation(self):
        if self.orientation is SHIP_ORIENTATION.HORIZONTAL:
            self.orientation = SHIP_ORIENTATION.VERTIKAL
        else:
            self.orientation = SHIP_ORIENTATION.HORIZONTAL


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

    def set_ship(self, ship: Ship):
        return False


class Player:

    def __init__(self, rules: dict):
        self.player_board = Board(rules["boardsize"])
        self.player_ships = self.__retrieve_ships_from_rules(rules["shipList"])

    def __retrieve_ships_from_rules(self, ships_to_create: dict):
        tmp_ship_list = []
        for key in ships_to_create.keys():
            tmp_ship_list.append([Ship(key) for i in range(ships_to_create[key])])
        return tuple(tmp_ship_list)

    def get_board(self):
        return self.player_board


class Game:
    gamerules = {
        "boardsize": 10,
        "shipList": {
            Ship_Type.SMALL: 3,
            Ship_Type.MEDIUM: 2,
            Ship_Type.BIG: 1
        }
    }

    def __init__(self):
        self.board1 = Board(10)
        self.playerA = Player(self.gamerules)
        self.playerB = Player(self.gamerules)

    def start_game(self):
        print("PlayerA:")
        self.playerA.get_board().print_board()
        print("\nPlayerB:")
        self.playerA.get_board().print_board()


game = Game()
game.start_game()
