import random
from BattleShips import Board
from appJar import gui


class Game:
    def __init__(self, appJar):
        self.board = Board(10).board

        self.gui = appJar
        self.gui.setTitle("Battleships")
        self.gui.setLocation("CENTER")

        self.gui.setImageLocation("./images")
        self.water = ["dark.gif", "medium.gif", "light.gif"]

    def fire_at_pos(self, title):
        self.gui.setImage(title, "fire.gif")

    def draw_board(self):

        self.gui.startLabelFrame("Game Board")

        for row in range(len(self.board)):
            for column in range(len(self.board)):
                self.gui.setSticky("nesw")
                self.gui.addImage(str(column) + ", " + str(row), random.choice(self.water), row, column)
                self.gui.setImageSubmitFunction(str(column) + ", " + str(row), self.fire_at_pos)

        self.gui.stopLabelFrame()


app = gui()

Game(app).draw_board()

app.go()
