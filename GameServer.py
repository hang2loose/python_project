import eventlet
import socketio
from BattleShips import Game

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

players_list = []
battle_ships = Game()


@sio.event
def connect(sid, environ):
    players_list.append(sid)
    print('connect ', sid)


@sio.event
def disconnect(sid):
    players_list.remove(sid)
    print('disconnect ', sid)


@sio.on('shoot_at')
def handle_player_shot(sid, payload):
    print("pizza " + payload)
    sio.emit('hit', payload, room=sid)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
