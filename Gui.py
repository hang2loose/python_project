import random
from BattleShips import Board
from appJar import gui


class Game:
    def __init__(self, appJar):
        self.board = Board(10).board
        self.gui = appJar
        self.gui.setTitle("Battleships")
        self.gui.setSize("800x600")
        self.gui.setLocation("CENTER")
        self.gui.setImageLocation("./images")
        self.water = ["dark.gif", "medium.gif", "light.gif"]

    def drawBoard(self):
        for entry in self.board:
            print(entry)
            self.gui.addImage(entry, random.choice(self.water))



app = gui()

Game(app).drawBoard()

app.go()
