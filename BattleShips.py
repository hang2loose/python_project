from BattleShipsEnums import *
import random


class Field:
    """
    :param __state: State of the field
    :type __statew: BattleShipsEnum
    """

    def __init__(self, ):
        self.__state = FIELD_STATE.EMPTY

    def change_field_state(self, state: FIELD_STATE):
        """
        changes state of field instanz
        :param state: new state
        """
        self.__state = state

    def print_field(self):
        """
        :return: value of the field enum from BattleShipsEnums.py
        """
        return self.__state.value

    def get_state(self):
        return self.__state


class Ship:
    """
    :param __occupied_fields: board fields which are occupied by the ship instance
    :param __size: size of the ship
    :param __orientation: Orientation of the ship can be horizontal or vertikal
    :param pos: position of the start of the ship ( x, y )
    """

    def __init__(self, ship_type: Ship_Type):
        self.__occupied_fields = []
        self.__size = ship_type.value
        self.__orientation = SHIP_ORIENTATION.HORIZONTAL
        self.pos = ()

    def is_ship_alive(self):
        """
        tests if the ship instance is still alive
        :return: true if at least one Field of the ship is still marked as SHIP_ALIVE
        """
        for field in self.__occupied_fields:
            if field.get_state() is FIELD_STATE.SHIP_ALIVE:
                return True
        return False

    def switch_orientation(self):
        """
        switches the orientation of the ship
        :default: HORIZONTAL
        :return:
        """
        if self.__orientation is SHIP_ORIENTATION.HORIZONTAL:
            self.__orientation = SHIP_ORIENTATION.VERTIKAL
        else:
            self.__orientation = SHIP_ORIENTATION.HORIZONTAL
        return self.__orientation

    def occupie_fields(self, ship_fields, pos):
        """
        Links the Ship instance to the designated Board
        :param ship_fields: board fields
        :param pos:
        """
        self.__occupied_fields = ship_fields
        self.pos = pos
        for field in self.__occupied_fields:
            field.change_field_state(FIELD_STATE.SHIP_ALIVE)

    def to_event(self):
        """
        :returns an dict with the ship informations to send to the Clients
        """
        return {
            "orientation": self.get_orientation().value,
            "size": self.get_size(),
            "pos": "{},{}".format(self.pos[0], self.pos[1])
        }

    def get_orientation(self):
        return self.__orientation

    def get_size(self):
        return self.__size


class Board:
    """
    :param __size: size of the board ( board is always square )
    """

    def __init__(self, size: int):
        self.__size = size
        self.__board = self.create_board()

    def print_board(self):
        """
        prints the board to the console
        """
        for row in self.__board:
            for field in row:
                print("{} ".format(field.print_field()), end='')
            print()

    def create_board(self):
        """
        creates an tuple of tuples of Field instances to represent an player board
        :return: an tuple of tuples with Field instances
        """
        return tuple([tuple([Field() for column in range(self.__size)]) for row in range(self.__size)])

    def set_ship_on_board(self, ship: Ship, pos: tuple):
        """
        Sets an ship instance onto the board
        :param ship: Ship instance
        :param pos: tuple of a x and y positions
        :returns: true if ship could be placed
        :returns: false if an error occurs and the ship could not be set on board
        """
        try:
            ship_fields = self.__get_ship_fields(ship, pos)
        except IndexError:
            print("Wanted ship position not in Bounds!!!")
            print("try again")
            return False
        for field in ship_fields:
            if field.get_state() is not FIELD_STATE.EMPTY:
                return False
        ship.occupie_fields(ship_fields, pos)
        return True

    def change_field_state(self, pos: tuple, new_state: FIELD_STATE):
        """
        changes the state of the field of the board
        :param pos: tuple of a x and y positions
        :param new_state: New State Enum for the field instance
        """
        self.__get_field(pos).change_field_state(new_state)

    def get_field_state(self, pos: tuple):
        return self.__get_field(pos).get_state()

    def __get_ship_fields(self, ship: Ship, pos: tuple):
        if ship.get_orientation() == SHIP_ORIENTATION.HORIZONTAL:
            return [self.__get_field((pos[0] + h, pos[1])) for h in range(ship.get_size())]
        return [self.__get_field((pos[0], pos[1] + v)) for v in range(ship.get_size())]

    def __get_field(self, pos: tuple):
        return self.__board[pos[1]][pos[0]]


class Player:
    """
    :param __player_board: board which holds the ships the player owns
    :param __enemy_board: board which holds represents the enemys board ( with the hits and misses of the player )
    :param __player_ships: a list of ships which the player owns
    """

    def __init__(self, rules: dict):
        """
        :param rules: game rules dict to initalize the game boards and ships
        """
        self.__player_board = Board(rules["boardsize"])
        self.__enemy_board = Board(rules["boardsize"])
        self.__player_ships = self.__retrieve_ships_from_rules(rules["shipList"])

    def print_player_board(self):
        """
        prints the player and enemy boards to the console
        """
        self.__player_board.print_board()
        print("---------------------")
        self.__enemy_board.print_board()

    def receive_shot(self, pos: tuple):
        """
        handles when a other player shoots at this player instance
        :param pos: tuple of a x and y position
        :returns: "hit" if a ship is hit
        :returns: "miss" if no ship hit
        """
        if self.__player_board.get_field_state(pos) is FIELD_STATE.SHIP_ALIVE:
            self.__player_board.change_field_state(pos, FIELD_STATE.SHIP_HIT)
            return "hit"
        self.__player_board.change_field_state(pos, FIELD_STATE.MISS)
        return "miss"

    def shoot_at(self, pos: tuple, player):
        """
        shots at a different player instance
        :param pos: tuple of a x and y position
        :param player: player instance which is shot at
        :returns: "hit" if shot is successfull
        :returns: "miss" if no ship is hit
        """
        event = player.receive_shot(pos)
        if event is "hit":
            self.__enemy_board.change_field_state(pos, FIELD_STATE.SHIP_HIT)
            return "hit"
        if self.__enemy_board.get_field_state(pos) is not FIELD_STATE.SHIP_HIT:
            self.__enemy_board.change_field_state(pos, FIELD_STATE.MISS)
            return "miss"

    def player_alive(self):
        """
        checks if the player instance still has atleast one ship alive
        :returns: True if there is still a ship alive
        :returns: False if there are no ships alive
        """
        for ship_type in self.__player_ships:
            for ship in ship_type:
                if ship.is_ship_alive():
                    return True
        return False

    def get_ship_events(self):
        """
        Returns a list of all ships and their informations to be send to the Client
        :return: an list of ships informatins
        """
        return [ship.to_event() for sublist in self.__player_ships for ship in sublist]

    def set_ships_random(self):
        """
        sets the ships from the player_ships list randomly on the player board
        """
        print("setting ships....hope you will be happy ;)")
        for ship in [ship for sublist in self.__player_ships for ship in sublist]:
            self.__randomly_switch_ship_orientation(ship)
            while not self.__player_board.set_ship_on_board(ship, self.__generate_random_pos()):
                self.__randomly_switch_ship_orientation(ship)

    def __generate_random_pos(self):
        """
        generates an random position tuple for a 10x10 board
        :return: tuple of two random ints from 0 to 10
        """
        return (random.randint(0, 9), random.randint(0, 9))

    def __randomly_switch_ship_orientation(self, ship: Ship):
        """
        switches the ship orientation randomly
        :param ship: ship instance
        """
        if random.randint(0, 100) % 2 is 1:
            ship.switch_orientation()

    def __retrieve_ships_from_rules(self, ships_to_create: dict):
        """
        generates the different ship instances from the game rules
        :param ships_to_create:
        :return: a tuple of ships instances
        """
        tmp_ship_list = []
        for key in ships_to_create.keys():
            tmp_ship_list.append([Ship(key) for i in range(ships_to_create[key])])
        return tuple(tmp_ship_list)


class Game:
    # pre configrued game rules
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
        self.player_A.set_ships_random()
        self.player_B.set_ships_random()

    def print_game_state(self):
        print("PlayerA:")
        self.player_A.print_player_board()
        print("\nPlayerB:")
        self.player_B.print_player_board()
