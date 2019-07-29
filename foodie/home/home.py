from Tkinter import *
cusines = ["Chinese", "Mexican", "Italian", "American"]

for cusine in cusines:
    c = Checkbutton(text=cusine)
    c.pack()
