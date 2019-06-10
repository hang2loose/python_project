import random
import socket
from BattleShips import Board
from appJar import gui

class Game:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, appJar):
        self.sock.connect(("127.0.0.1", 8080))
        self.msg = ""

        self.board = Board(10).board

        self.gui = appJar
        self.gui.setTitle("Battleships")
        self.gui.setLocation("CENTER")

        self.gui.setImageLocation("./images")
        self.water = ["dark.gif", "medium.gif", "light.gif"]

        self.gui.thread(self.get)

    def get(self):
        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            self.gui.setImage(str(data, 'utf-8'), "fire.gif")

    def set(self, title):
        self.sock.send(bytes(title, 'utf-8'))

    def draw_board(self):

        self.gui.startLabelFrame("Game Board")

        for row in range(len(self.board)):
            for column in range(len(self.board)):
                self.gui.setSticky("nesw")
                self.gui.addImage("{},{}".format(column, row), random.choice(self.water), column, row)
                self.gui.setImageSubmitFunction("{},{}".format(column, row), self.set)

        self.gui.stopLabelFrame()


app = gui()
Game(app).draw_board()
app.go()
