import random
import socket

from appJar import gui


class GUI:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, appJar):
        self.sock.connect(("127.0.0.1", 8080))

        self.state = "game"

        self.gui = appJar
        self.gui.setTitle("Battleships")
        self.gui.setLocation("CENTER")

        self.gui.setImageLocation("./Client/images")
        self.water = ["dark.gif", "medium.gif", "light.gif"]

        self.gui.thread(self.receive)

    def receive(self):
        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            self.gui.setImage(str(data, 'utf-8'), "fire.gif")

    def send(self, title):
        self.sock.send(bytes(title, 'utf-8'))

    def set(self, pos):
        pass

    def board(self):
        return 10

    def hit(self, pos):
        pass

    def miss(self, pos):
        pass

    def draw_framework(self):
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
