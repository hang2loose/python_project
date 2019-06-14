import random
import socket
import json
from appJar import gui


class ConnectionHandler:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, parser):
        self.sock.connect(("127.0.0.1", 8080))
        self.parser = parser

    def receive(self):
        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            self.parser.receive_data(str(data, 'utf-8'))

    def send(self, data):
        self.sock.send(bytes(data, 'utf-8'))


class Parser:
    def __init__(self, functions: dict):
        self.functions = functions
        self.connection_handler = ConnectionHandler(self)

    def listener(self):
        self.connection_handler.receive()

    def extract(self, event, load):
        self.functions[event].__call__(load)

    def receive_data(self, data):
        data = json.loads(data)
        self.extract(data["event"], str(data["load"]))

    def send_data(self, pos, state):
        data = {
            "state": state,
            "event": "hit",
            "load": pos
        }
        self.connection_handler.send(json.dumps(data))



class GUI:
    def __init__(self, framework):
        self.gui = framework
        self.coords = {}
        self.state = "game"

        self.water = [
            "dark.gif",
            "medium.gif",
            "light.gif"
        ]

        self.functions = {
            "board": self.board,
            "set": self.set,
            "hit": self.hit,
            "miss": self.miss
        }

        self.parser = Parser(self.functions)

        self.gui.thread(self.parser.listener)

    def set(self, pos):
        if pos[:7] != "UNKNOWN":
            self.parser.send_data(pos, self.state)

    def board(self):
        return 10

    def hit(self, pos):
        self.gui.addCanvasImage("Board", self.coords[pos][0] + 16, self.coords[pos][1] + 16, "hit.gif")

    def miss(self, pos):
        self.gui.addCanvasImage("Board", self.coords[pos][0] + 16, self.coords[pos][1] + 16, "miss.gif")

    def draw_parameters(self):
        self.gui.setTitle("Battleships")
        self.gui.setResizable(canResize=False)
        self.gui.setLocation("CENTER")

        self.gui.setStretch("None")
        self.gui.setGuiPadding(100, 20)
        self.gui.setImageLocation("./Client/images")

    def draw_board(self):
        self.gui.startFrame("Game", 1)

        self.gui.addCanvas("Board")
        self.gui.setCanvasWidth("Board", 352)
        self.gui.setCanvasHeight("Board", 352)

        self.gui.addCanvasImage("Board", 192, 16, "top_bar.gif")
        self.gui.addCanvasImage("Board", 16, 192, "left_bar.gif")

        x = 16
        for row in range(self.board()):
            x += 32
            y = 16
            for column in range(self.board()):
                y += 32
                self.gui.addCanvasImage("Board", x, y, random.choice(self.water))
                self.coords.update({"{},{}".format(row, column): [x-16, y-16, x+16, y+16]})

        self.gui.setCanvasMap("Board", self.set, self.coords)

        self.gui.stopFrame()

    def draw(self):
        self.draw_parameters()

        self.gui.startLabelFrame("State", 0)
        self.gui.addLabel("l1", "Label 1")
        self.gui.stopLabelFrame()

        self.draw_board()

        self.gui.startLabelFrame("Logic", 2)
        self.gui.addLabel("l2", "Label 2")
        self.gui.stopLabelFrame()


app = gui()
GUI(app).draw()
app.go()
