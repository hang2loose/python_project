import random
from tkinter import *


class Battleships:
    def __init__(self):
        self.water1 = PhotoImage(file="water_01.gif")
        self.water2 = PhotoImage(file="water_02.gif")
        self.water3 = PhotoImage(file="water_03.gif")

        self.fire = PhotoImage(file="fire.gif")

        self.water = [self.water1, self.water2, self.water3]

        self.button = Button(root, image=random.choice(self.water), height=32, width=32,
                             command=lambda: root.config(image=self.fire)).grid(row=1)


root = Tk()

Label(root, text="Header").grid(row=0, columnspan=10)

Label(root, text="Content").grid(row=1)
app = Battleships()

Label(root, text="Footer").grid(row=11, columnspan=10)

mainloop()
