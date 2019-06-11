import random
import socket
import json
from appJar import gui


class Handler:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, parser):
        self.sock.connect(("127.0.0.1", 8080))
        self.parser = parser

    def receive(self):
        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            self.parser.receive(str(data, 'utf-8'))

    def send(self, data):
        self.sock.send(bytes(data, 'utf-8'))


class Parser:
    def __init__(self, functions: dict):
        self.functions = functions

    def extract(self, event, load):
        self.functions[event].__call__(load)

    def receive(self, data):
        data = json.loads(data)
        self.extract(data["event"], str(data["load"]))

    def send(self, pos, state):
        data = {
            "state": state,
            "event": "hit",
            "load": pos
        }
        self.functions["send"].__call__(json.dumps(data))


class GUI:
    def __init__(self, appJar):
        self.gui = appJar

        self.functions = {
            "board": self.board,
            "set": self.set,
            "hit": self.hit,
            "miss": self.miss
        }

        self.parser = Parser(self.functions)
        self.handler = Handler(self.parser)

        self.functions.update({"send": self.handler.send})

        self.state = "game"
        self.gui.setImageLocation("./Client/images")
        self.water = ["dark.gif", "medium.gif", "light.gif"]

        self.gui.thread(self.handler.receive)

    def set(self, pos):
        self.parser.send(pos, self.state)

    def board(self):
        return 10

    def hit(self, pos):
        self.gui.setImage(pos, "hit.gif")

    def miss(self, pos):
        self.gui.setImage(pos, "miss.gif")

    def draw_framework(self):
        self.gui.setTitle("Battleships")
        self.gui.setLocation("CENTER")

        self.gui.startLabelFrame("State", 0)
        self.gui.addLabel("l1", "Label 1")
        self.gui.stopLabelFrame()

        self.gui.startLabelFrame("Logic", 2)
        self.gui.addLabel("l2", "Label 2")
        self.gui.stopLabelFrame()

    def draw_board(self):
        self.gui.startLabelFrame("Game Board", 1)

        for row in range(self.board()):
            for column in range(self.board()):
                self.gui.addImage("{},{}".format(column, row), random.choice(self.water), column, row)
                self.gui.setImageSubmitFunction("{},{}".format(column, row), self.set)

        self.gui.stopLabelFrame()


app = gui()
gui = GUI(app)
gui.draw_framework()
gui.draw_board()
app.go()
