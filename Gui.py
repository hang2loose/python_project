import random
import Board
from tkinter import *


class Battleships:
    def __init__(self):
        self.water1 = PhotoImage(file="water_01.gif")
        self.water2 = PhotoImage(file="water_02.gif")
        self.water3 = PhotoImage(file="water_03.gif")

        self.water = [self.water1, self.water2, self.water3]

        self.fire = PhotoImage(file="fire.gif")

        self.button1 = Button(root, image=random.choice(self.water), height=32, width=32,
              command=lambda: self.button1.configure(image=self.fire))

        self.button1.grid(row=2, column=2)

    def generate_button(self):
        return Button(root, image=random.choice(self.water), height=32, width=32, command=lambda: this.configure(image=self.fire))

    def draw_board(self, board):
        game_board = [self.generate_button() for entry in range(board)]

        print(game_board)

        for x in range(board):
            game_board[x].grid(row=x)

        return game_board


root = Tk()
root.wm_state('zoomed')
root.title('Battleships')


Label(root, text="Header").grid(row=0, columnspan=10)

Label(root, text="Content").grid(row=1)
app = Battleships().draw_board(10)

Label(root, text="Footer").grid(row=11, columnspan=10)

mainloop()
