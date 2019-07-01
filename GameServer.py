import eventlet
import socketio
from BattleShips import Game

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

players_list = []
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

active_player = battle_ships.player_A


@sio.event
def connect(sid, environ):
    players_list.append(sid)
    print('connect ', sid)
    if len(players_list) is 1:
        players[battle_ships.player_A]["sid"] = sid
        sio.emit('player', 'Waiting for Player...', sid)
    if len(players_list) is 2:
        players[battle_ships.player_B]["sid"] = sid

        # starts game after 2 players are connected ( all other connections will be ignored )
        start_game()


@sio.event
def disconnect(sid):
    players_list.remove(sid)
    print('disconnect ', sid)


@sio.on('shoot_at')
def handle_player_shot(sid, payload):
    global active_player
    print("pizza " + payload)
    if active_player is get_player_from_sid(sid):
        shooting_player = get_player_from_sid(sid)
        active_player = player_shoot_at_player(shooting_player, payload)

    # battle_ships.print_game_state()


@sio.on('get_ships')
def get_ships(sid):
    print('getting ships..')
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
    battle_ships.start_game()


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
