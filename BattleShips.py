from BattleShipsEnums import *


class Field:
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
        for field in self.occupied_fields:
            if field.state is FIELD_STATE.SHIP_ALIVE:
                return True
        return False

    def switch_orientation(self):
        if self.orientation is SHIP_ORIENTATION.HORIZONTAL:
            self.orientation = SHIP_ORIENTATION.VERTIKAL
        else:
            self.orientation = SHIP_ORIENTATION.HORIZONTAL
        return self.orientation


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

    def set_ship_on_board(self, ship: Ship, pos: tuple):
        return False

    def get_field(self, pos: tuple):
        return self.board[pos[0]][pos[1]]


class Player:

    def __init__(self, rules: dict):
        self.player_board = Board(rules["boardsize"])
        self.player_ships = self.__retrieve_ships_from_rules(rules["shipList"])

    def __retrieve_ships_from_rules(self, ships_to_create: dict):
        tmp_ship_list = []
        for key in ships_to_create.keys():
            tmp_ship_list.append([Ship(key) for i in range(ships_to_create[key])])
        return tuple(tmp_ship_list)

    def print_player_board(self):
        return self.player_board.print_board()

    def recive_shot(self, pos: tuple):
        field = self.player_board.get_field(pos)

        if field.state is FIELD_STATE.SHIP_ALIVE:
            field.change_field_state(FIELD_STATE.SHIP_HIT)
            return "hit"
        return "miss"

    def shoot_at(self, pos: tuple, player):
        field = self.player_board.get_field(pos)
        event = player.recive_shot(pos)
        if event is "hit":
            field.change_field_state(FIELD_STATE.SHIP_HIT)
            return
        field.change_field_state(FIELD_STATE.MISS)
        return

    def player_alive(self):
        for ship_type in self.player_ships:
            for ship in ship_type:
                if ship.is_ship_alive():
                    return True
        return False

    def set_ships_on_board(self, ship: Ship, pos: tuple):
        if self.player_board.set_ship_on_board(ship, pos) is True:
            return True
        return False


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
        self.player_A = Player(self.gamerules)
        self.player_B = Player(self.gamerules)

    def start_game(self):
        player_a_turn = True
        while True:
            pos = (int(input("x: ")), int(input("y: ")))
            if player_a_turn:
                self.player_A.shoot_at(pos, self.player_B)
            else:
                self.player_B.shoot_at(pos, self.player_A)
            self.print_game_state()
            player_a_turn = not player_a_turn

    def print_game_state(self):
        print("PlayerA:")
        self.player_A.print_player_board()
        print("\nPlayerB:")
        self.player_B.print_player_board()


game = Game()
game.start_game()
