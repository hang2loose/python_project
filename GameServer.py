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
        "sid": players_list[0]
    },
    battle_ships.player_B: {
        "enemy": battle_ships.player_A,
        "sid": players_list[1]
    }
}


@sio.event
def connect(sid, environ):
    players_list.append(sid)
    if len(players_list) is 1:
        players[battle_ships.player_A]["sid"] = sid
        sio.emit('player', 'Waiting for Player...', sid)
    if len(players_list) is 2:
        players[battle_ships.player_B]["sid"] = sid
    print('connect ', sid)


@sio.event
def disconnect(sid):
    players_list.remove(sid)
    print('disconnect ', sid)


@sio.on('shoot_at')
def handle_player_shot(sid, payload):
    print("pizza " + payload)
    pos = tuple(int(p) for p in payload.split(','))
    sio.emit(battle_ships.player_A.shoot_at(pos, battle_ships.player_B), payload, sid)
    battle_ships.print_game_state()


def player_shoot_at_player(player, payload):
    player_enemy = players[player]["enemy"]
    player_sid = players[player]["sid"]
    enemy_sid = players[player_enemy]["sid"]

    # convert payload to position tuple
    pos = tuple(int(p) for p in payload.split(','))

    shoot_result = battle_ships.player.shoot_at(pos, player_enemy)

    # emit result to shooting player
    sio.emit(shoot_result, payload, player_sid)

    # emit result to enemy
    sio.emit("ship_"+shoot_result, payload, enemy_sid)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
