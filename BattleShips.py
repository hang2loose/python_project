from BattleShipsEnums import *


class Field:
    def __init__(self, ):
        self.__state = FIELD_STATE.EMPTY

    def change_field_state(self, state: FIELD_STATE):
        self.__state = state

    def print_field(self):
        return self.__state.value

    def get_state(self):
        return self.__state


class Ship:

    def __init__(self, ship_type: Ship_Type):
        self.__occupied_fields = []
        self.__size = ship_type.value
        self.__orientation = SHIP_ORIENTATION.HORIZONTAL

    def is_ship_alive(self):
        for field in self.__occupied_fields:
            if field.state is FIELD_STATE.SHIP_ALIVE:
                return True
        return False

    def switch_orientation(self):
        if self.__orientation is SHIP_ORIENTATION.HORIZONTAL:
            self.__orientation = SHIP_ORIENTATION.VERTIKAL
        else:
            self.__orientation = SHIP_ORIENTATION.HORIZONTAL
        return self.__orientation

    def occupie_fields(self, ship_fields):
        self.__occupied_fields = ship_fields
        for field in self.__occupied_fields:
            field.change_field_state(FIELD_STATE.SHIP_ALIVE)

    def get_orientation(self):
        return self.__orientation

    def get_size(self):
        return self.__size


class Board:
    def __init__(self, size: int):
        self.__size = size
        self.__board = self.create_board()

    def create_board(self):
        return tuple([tuple([Field() for column in range(self.__size)]) for row in range(self.__size)])

    def print_board(self):
        for row in self.__board:
            for field in row:
                print("{} ".format(field.print_field()), end='')
            print()

    def set_ship_on_board(self, ship: Ship, pos: tuple):
        ship_fields = self.__get_ship_fields(ship, pos)
        for field in ship_fields:
            if field.get_state() is not FIELD_STATE.EMPTY:
                return False
        ship.occupie_fields(ship_fields)

    def __get_ship_fields(self, ship: Ship, pos: tuple):
        tmp = []
        if ship.get_orientation() == SHIP_ORIENTATION.HORIZONTAL:
            for h in range(ship.get_size()):
                tmp.append(self.get_field((0,h)))
        #return [self.__board[pos[v][pos[1]]] for v in range(ship.get_size() - 1)]
        return tuple(tmp)

    def get_field(self, pos: tuple):
        return self.__board[pos[0]][pos[1]]


class Player:

    def __init__(self, rules: dict):
        self.__player_board = Board(rules["boardsize"])
        self.__player_ships = self.__retrieve_ships_from_rules(rules["shipList"])

    def __retrieve_ships_from_rules(self, ships_to_create: dict):
        tmp_ship_list = []
        for key in ships_to_create.keys():
            tmp_ship_list.append([Ship(key) for i in range(ships_to_create[key])])
        return tuple(tmp_ship_list)

    def print_player_board(self):
        return self.__player_board.print_board()

    def recive_shot(self, pos: tuple):
        field = self.__player_board.get_field(pos)

        if field.get_state() is FIELD_STATE.SHIP_ALIVE:
            field.change_field_state(FIELD_STATE.SHIP_HIT)
            return "hit"
        return "miss"

    def shoot_at(self, pos: tuple, player):
        field = self.__player_board.get_field(pos)
        event = player.recive_shot(pos)
        if event is "hit":
            field.change_field_state(FIELD_STATE.SHIP_HIT)
            return
        field.change_field_state(FIELD_STATE.MISS)
        return

    def player_alive(self):
        for ship_type in self.__player_ships:
            for ship in ship_type:
                if ship.is_ship_alive():
                    return True
        return False

    def set_ships_on_board(self):
        ship = self.__player_ships[0][0]
        pos = (0,0)
        if self.__player_board.set_ship_on_board(ship, pos) is True:
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
        self.player_A.set_ships_on_board()
        self.print_game_state()
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
