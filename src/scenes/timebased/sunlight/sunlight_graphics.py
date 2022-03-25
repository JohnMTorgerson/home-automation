# import graphics as g
from tkinter import *
import random
from .spec_to_rgb.convert_color import get_color

w = 600 # window width
h = 400 # window height

warmest = 2400
coldest = 5900

# def open() :
#     win = g.GraphWin("Sunlight Scene",w,h)
#     print('window opened')
#     draw_gradient_bg(win)
#
#
#     win.getMouse()
#     win.close()

def open() :
    # Create an instance of tkinter frame or window
    root=Tk()

    # Set the size of the tkinter window
    root.geometry(f"{w}x{h}")

    # Create a canvas widget
    canvas=Canvas(root, width=500, height=300)
    canvas.pack()

    # Add a line in canvas widget
    canvas.create_line(100,200,200,35, fill="green", width=5)

    text = Text(root)
    text.insert(INSERT, "Hello.....")
    text.insert(END, "Bye Bye.....")
    text.pack()
    text.tag_add("here", "1.0", "1.4")
    text.tag_add("start", "1.8", "1.13")
    text.tag_config("here", background="yellow", foreground="blue")
    text.tag_config("start", background="black", foreground="green")

    root.title('boobs')
    root.mainloop()


def draw_gradient_bg(canvas) :
    for row in range(h) :
        # line = g.Line(g.Point(0, row), g.Point(w, row)) # horizontal line from zero to window width at y coord <row>
        temp = row / h * (coldest - warmest) + warmest
        print(temp)
        color = get_color(temp)
        print(color)
        # line.setOutline(g.color_rgb(random.randrange(256),random.randrange(256),random.randrange(256)))
        # line.setWidth(1)
        # line.draw(win)

        canvas.create_line(0,row,w,row, fill="green", width=1)
