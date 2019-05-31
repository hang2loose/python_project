import random
from tkinter import *

root = Tk()

water1 = PhotoImage(file="water_01.gif")
water2 = PhotoImage(file="water_02.gif")
water3 = PhotoImage(file="water_03.gif")

water = [water1, water2, water3]
fire = PhotoImage(file="fire.gif")

Label(root, text="Header").grid(row=0, columnspan=10)

Label(root, text="Content").grid(row=1)

Button(root, image=random.choice(water), height=32, width=32).grid(row=1).bind("<Button-1>")


Label(root, text="Footer").grid(row=11, columnspan=10)

mainloop()
