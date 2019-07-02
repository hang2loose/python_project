import eventlet
import socketio
from BattleShips import Game

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

players_list = []
game_dict = {}
players_dict = {}
game_name = None
game_id = 0


def game_id_generator():
    global game_id
    while True:
        game_id += 1
        yield


@sio.event
def connect(sid, environ):
    global game_name
    players_list.append(sid)
    print('connect ', sid)

    if len(players_list) % 2 == 1:
        game_name = 'game_room_{}'.format(game_id)
        sio.enter_room(sid, game_name)
        game_dict.update({game_name: Game()})
        players_dict.update(
            {game_name: {
                game_dict[game_name].player_A: {
                    "enemy": game_dict[game_name].player_B,
                    "sid": sid
                }
            }}
        )

    if len(players_list) % 2 == 0:
        sio.enter_room(sid, game_name)
        players_dict[game_name].update({
                game_dict[game_name].player_B: {
                    "enemy": game_dict[game_name].player_A,
                    "sid": sid
                }
            }
        )
        # starts game after 2 players are connected to the same game room
        start_game(game_name)
        game_id_generator().__next__()

    sio.emit('game_room', game_name, sid)


@sio.event
def disconnect(sid):
    game_room = next((room for room, entry in players_dict.items() for key, value in entry.items() if value["sid"] == sid), None)

    if players_dict[game_room][game_dict[game_room].player_A]["sid"] == sid:
        sio.emit('game_over', 'win', players_dict[game_room][game_dict[game_room].player_B]["sid"])
    if players_dict[game_room][game_dict[game_room].player_B]["sid"] == sid:
        sio.emit('game_over', 'win', players_dict[game_room][game_dict[game_room].player_A]["sid"])

    # TODO: Listen Aufräumen
    # players_list.remove(sid)
    print('disconnect ', sid)


@sio.on('shoot_at')
def handle_player_shot(sid, payload):
    print(payload)
    if players_dict[payload["game_room"]]["active"] is get_player_from_sid(sid, payload["game_room"]):
        shooting_player = get_player_from_sid(sid, payload["game_room"])
        players_dict[payload["game_room"]].update({"active": player_shoot_at_player(shooting_player, payload)})
        if players_dict[payload["game_room"]]["active"].player_alive():
            sio.emit('turn', 'turn', players_dict[payload["game_room"]][players_dict[payload["game_room"]]["active"]]["sid"])
        else:
            game_over(payload["game_room"])


@sio.on('gui_loaded')
def gui_loaded(sid, payload):
    print(payload)
    if len(players_dict[payload]) is 1:
        sio.emit('player', 'wait', sid)
    if len(players_dict[payload]) is 3:
        sio.emit('player', 'start', players_dict[payload][game_dict[payload].player_A]["sid"])
        sio.emit('turn', 'wait', players_dict[payload][game_dict[payload].player_B]["sid"])

    print('sending ships..')
    for ship_event in get_player_from_sid(sid, payload).get_ship_events():
        sio.emit("ship", ship_event, sid)


def player_shoot_at_player(player, payload):
    player_enemy = players_dict[payload["game_room"]][player]["enemy"]
    player_sid = players_dict[payload["game_room"]][player]["sid"]
    enemy_sid = players_dict[payload["game_room"]][player_enemy]["sid"]

    # convert payload to position tuple
    pos = tuple(int(p) for p in payload["pos"].split(','))

    shoot_result = player.shoot_at(pos, player_enemy)

    # emit result to shooting player
    sio.emit(shoot_result, payload["pos"], player_sid)

    # emit result to enemy
    sio.emit("ship_" + shoot_result, payload["pos"], enemy_sid)

    return player_enemy


def get_player_from_sid(sid, room):
    for player in players_dict[room]:
        if players_dict[room][player]["sid"] is sid:
            return player


def start_game(room):
    players_dict[room].update({"active": game_dict[room].player_A})


def game_over(room):
    if not game_dict[room].player_A.player_alive():
        sio.emit('game_over', 'loose', players_dict[room][game_dict[room].player_A]["sid"])
        sio.emit('game_over', 'win', players_dict[room][game_dict[room].player_B]["sid"])
    if not game_dict[room].player_B.player_alive():
        sio.emit('game_over', 'win', players_dict[room][game_dict[room].player_A]["sid"])
        sio.emit('game_over', 'loose', players_dict[room][game_dict[room].player_B]["sid"])


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
