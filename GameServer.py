import eventlet
import socketio
from BattleShips import Game

# Socket-io Server initialization
sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

# Simple list of ID's generated by socket-io (sid)
players_list = []

# Dictionary of game rooms:
# game_dict {
#       "game_room": Game_Instance
# }
game_dict = {}

# Dictionary of players in game rooms:
# players_dict {
#         "game_room": {
#                "game_room.player_a": {
#                               "enemy": game_room.player_b,
#                               "sid": socket_io_id
#                },
#                "game_room.player_b": {
#                               "enemy": game_room.player_b,
#                               "sid": socket_io_id
#                }
#                "active": active_player
#         }
# }
players_dict = {}


def game_id_generator():
    """
    ID generator to make the game room name unique
    """
    game_id_var = 0
    while True:
        yield game_id_var
        game_id_var += 1


# Variables to build the unique game room name
game_room_name = None
game_id = game_id_generator()


@sio.event
def connect(sid, environ):
    """
    Socket-io event fired when users connect to the Server
    :param sid: socket-io id
    :param environ: connection information
    """
    global game_room_name
    players_list.append(sid)
    print('connect ', sid)

    # Odd player_list: generate new game room and add the connected player
    if len(players_list) % 2 == 1:
        game_room_name = 'game_room_{}'.format(game_id.__next__())
        sio.enter_room(sid, game_room_name)
        game_dict.update({game_room_name: Game()})
        players_dict.update(
            {game_room_name: {
                game_dict[game_room_name].player_A: {
                    "enemy": game_dict[game_room_name].player_B,
                    "sid": sid
                },
                game_dict[game_room_name].player_B: {
                    "enemy": game_dict[game_room_name].player_A,
                    "sid": None
                },
                "active": None
            }}
        )
        print("Added 1st player to {}".format(game_room_name))

    # Even player_list: add connected player to the last generated game room
    if len(players_list) % 2 == 0:
        sio.enter_room(sid, game_room_name)
        players_dict[game_room_name][game_dict[game_room_name].player_B]["sid"] = sid
        print("Added 2nd player to {}".format(game_room_name))

        # Starts game after 2 players are connected to the same game room
        start_game(game_room_name)

    # Send the players game room name to the client on connection
    sio.emit('game_room', game_room_name, sid)


@sio.event
def disconnect(sid):
    """
    Socket-io event fired when users loose connection
    :param sid: socket-io id
    """
    game_room = next((room for room, entry in players_dict.items()
                      for key, value in entry.items() if value["sid"] == sid), None)

    player_a_sid = players_dict[game_room][game_dict[game_room].player_A]["sid"]
    player_b_sid = players_dict[game_room][game_dict[game_room].player_B]["sid"]

    # send win event to the connected player and disconnect them
    if player_a_sid == sid:
        sio.emit('game_over', 'win', player_b_sid)
        sio.disconnect(player_b_sid)
    if player_b_sid == sid:
        sio.emit('game_over', 'win', player_a_sid)
        sio.disconnect(player_a_sid)

    # clean up the players list
    if player_a_sid is not None:
        players_list.remove(player_a_sid)
    if player_b_sid is not None:
        players_list.remove(player_b_sid)

    # dictionary clean up
    del game_dict[game_room]
    del players_dict[game_room]

    print('disconnect ', sid)


@sio.on('shoot_at')
def handle_player_shot(sid, payload):
    """
    Socket-io listening for the shoot at event fired from client
    :param sid: socket-io id
    :param payload: message send by client
    """
    print(payload)
    # Check is event sending player also active player
    if players_dict[payload["game_room"]]["active"] is get_player_from_sid(sid, payload["game_room"]):
        shooting_player = get_player_from_sid(sid, payload["game_room"])
        # Shoot and change active player
        players_dict[payload["game_room"]].update({"active": player_shoot_at_player(shooting_player, payload)})
        if players_dict[payload["game_room"]]["active"].player_alive():
            # Tell players who is the active player
            sio.emit('turn', 'turn', players_dict[payload["game_room"]][players_dict[payload["game_room"]]["active"]]["sid"])
        else:
            game_over(payload["game_room"])


@sio.on('gui_loaded')
def gui_loaded(sid, payload):
    """
    Socket.io waiting for gui loaded event to send initial game information
    :param sid: socket-io id
    :param payload: message send by client
    """
    print(payload)
    if players_dict[payload][game_dict[payload].player_B]["sid"] is None:
        sio.emit('player', 'wait', sid)
    else:
        sio.emit('player', 'start', players_dict[payload][game_dict[payload].player_A]["sid"])
        sio.emit('turn', 'wait', players_dict[payload][game_dict[payload].player_B]["sid"])

    print('sending ships..')
    for ship_event in get_player_from_sid(sid, payload).get_ship_events():
        sio.emit("ship", ship_event, sid)


def player_shoot_at_player(player, payload):
    """
    Players shooting at each other -> Translation from server events to game logic
    :param player: player object
    :param payload: message send by client
    :return: enemy player object
    """
    player_enemy = players_dict[payload["game_room"]][player]["enemy"]
    player_sid = players_dict[payload["game_room"]][player]["sid"]
    enemy_sid = players_dict[payload["game_room"]][player_enemy]["sid"]

    # Convert payload to position tuple
    pos = tuple(int(p) for p in payload["pos"].split(','))

    shoot_result = player.shoot_at(pos, player_enemy)

    # Send result to shooting player
    sio.emit(shoot_result, payload["pos"], player_sid)

    # Send result to enemy
    sio.emit("ship_" + shoot_result, payload["pos"], enemy_sid)

    return player_enemy


def get_player_from_sid(sid, room):
    """
    Getting the player for the game logic through the socket-io ID from the players_dict
    :param sid: socket-io id
    :param room: game room
    :return: player object
    """
    for player in players_dict[room]:
        if players_dict[room][player]["sid"] is sid:
            return player


def start_game(room):
    """
    Set the first active player to start the game
    :param room: game room
    """
    players_dict[room].update({"active": game_dict[room].player_A})


def game_over(room):
    """
    Send the win/loose event to the players
    :param room: game room
    """
    if not game_dict[room].player_A.player_alive():
        sio.emit('game_over', 'loose', players_dict[room][game_dict[room].player_A]["sid"])
        sio.emit('game_over', 'win', players_dict[room][game_dict[room].player_B]["sid"])
    if not game_dict[room].player_B.player_alive():
        sio.emit('game_over', 'win', players_dict[room][game_dict[room].player_A]["sid"])
        sio.emit('game_over', 'loose', players_dict[room][game_dict[room].player_B]["sid"])


# Start the server with eventlet
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
