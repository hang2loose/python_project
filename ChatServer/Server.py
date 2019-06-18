import socket
import json
import threading


class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []

    def __init__(self):
        self.sock.bind(('0.0.0.0', 8080))
        self.sock.listen(1)

    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            print(str(data))
            for connection in self.connections:
                self.send_to_client("hit", "1,1", connection)
                if not data:
                    print(str(a[0]) + ":" + str(a[1]), "disconnected")
                    self.connections.remove(c)
                    c.close()
                    break

    def run(self):
        while True:
            c, a = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            print(str(a[0]) + ":" + str(a[1]), "connected")

    def send_to_client(self, event_type: str, pos: str, connection):
        connection.send(bytes(json.dumps(self.__event_builder(event_type, pos)), 'utf-8'))

    def __event_builder(self, event_type: str, pos: str):
        return {
            "state": "game",
            "event_type": event_type,
            "pos": pos
        }


server = Server()
server.run()
