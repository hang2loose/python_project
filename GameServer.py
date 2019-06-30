import eventlet
import socketio
from BattleShips import Game

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

battle_ships = Game()


@sio.event
def connect(sid, environ):
    print('connect ', sid)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


@sio.on('shoot_at')
def handle_player_shot(sid, payload):
    print("pizza " + payload)
    battle_ships.print_game_state()
    sio.emit('miss', payload)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
