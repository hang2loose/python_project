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


battle_ships = Game()

players = {
    battle_ships.player_A: {
        "enemy": battle_ships.player_B,
        "sid": None
    },
    battle_ships.player_B: {
        "enemy": battle_ships.player_A,
        "sid": None
    }
}

active_player = None


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
        game_id_generator().__next__()

    sio.emit('game_room', game_name, sid)

    if len(players_list) is 1:
        players[battle_ships.player_A]["sid"] = sid
    if len(players_list) is 2:
        players[battle_ships.player_B]["sid"] = sid

        # starts game after 2 players are connected ( all other connections will be ignored )
        start_game()


@sio.event
def disconnect(sid):
    if players[battle_ships.player_A]["sid"] == sid:
        sio.emit('game_over', 'win', players[battle_ships.player_B]["sid"])
    if players[battle_ships.player_B]["sid"] == sid:
        sio.emit('game_over', 'win', players[battle_ships.player_A]["sid"])
    players_list.remove(sid)
    print('disconnect ', sid)


@sio.on('shoot_at')
def handle_player_shot(sid, payload):
    global active_player
    print("pizza " + payload)
    if active_player is get_player_from_sid(sid):
        shooting_player = get_player_from_sid(sid)
        active_player = player_shoot_at_player(shooting_player, payload)
        if active_player.player_alive():
            sio.emit('turn', 'turn', players[active_player]["sid"])
        else:
            game_over()


@sio.on('gui_loaded')
def gui_loaded(sid):
    if len(players_list) is 1:
        sio.emit('player', 'wait', sid)
    if len(players_list) is 2:
        sio.emit('player', 'start', players[battle_ships.player_A]["sid"])
        sio.emit('turn', 'wait', players[battle_ships.player_B]["sid"])

    print('sending ships..')
    for ship_event in get_player_from_sid(sid).get_ship_events():
        sio.emit("ship", ship_event, sid)


def player_shoot_at_player(player, payload):
    player_enemy = players[player]["enemy"]
    player_sid = players[player]["sid"]
    enemy_sid = players[player_enemy]["sid"]

    # convert payload to position tuple
    pos = tuple(int(p) for p in payload.split(','))

    shoot_result = player.shoot_at(pos, player_enemy)

    # emit result to shooting player
    sio.emit(shoot_result, payload, player_sid)

    # emit result to enemy
    sio.emit("ship_" + shoot_result, payload, enemy_sid)

    return player_enemy


def get_player_from_sid(sid):
    for player in players:
        if players[player]["sid"] is sid:
            return player


def start_game():
    global active_player
    active_player = battle_ships.player_A


def game_over():
    if not battle_ships.player_A.player_alive():
        sio.emit('game_over', 'loose', players[battle_ships.player_A]["sid"])
        sio.emit('game_over', 'win', players[battle_ships.player_B]["sid"])
    if not battle_ships.player_B.player_alive():
        sio.emit('game_over', 'win', players[battle_ships.player_A]["sid"])
        sio.emit('game_over', 'loose', players[battle_ships.player_B]["sid"])


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
