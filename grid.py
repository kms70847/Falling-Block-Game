from Tkinter import *
from geometry import Point
from PIL import Image, ImageTk

#upgraded form of Canvas.

#Canvas that can be used to draw grid-locked sprites.
#(0,0) is the lower left of the grid.

def get_sprite(name):
    """
        creates a TkImage instance from the given name.
        each name should correspond to an png in the images directory, minus the file extension.
    """
    return ImageTk.PhotoImage(Image.open("images/{}.png".format(name)))

class Grid(Canvas):
    def __init__(self, root, **kargs):
        self.length = kargs.pop("length", 16)
        self.cols = kargs.pop("cols", 10)
        self.rows = kargs.pop("rows", 22) #typically 16 to 24

        self.margin = 10

        width = self.cols * self.length + self.margin * 2
        height = self.rows * self.length + self.margin * 2

        bg = kargs.pop("background_color", (255,255,255))

        kargs["width"] = width
        kargs["height"] = height
        Canvas.__init__(self, root, **kargs)

        self.background = self.create_rectangle(self.margin, self.margin, width-self.margin, height-self.margin)
        self.set_background(bg)


        #maps sprite names to ImageTk instances.
        #don't let these get garbage collected while the Canvas is alive!
        self.sprites = {}

        #maps points to canvas ids
        self.tile_ids = {}

        #maps points to sprite names
        self.tile_names = {}


    def set(self, p, name):
        if name == None:
            self.remove(p)
            return
        self.tile_names[p] = name
        if name not in self.sprites:
            self.sprites[name] = get_sprite(name)

        if p not in self.tile_ids:
            left = self.margin + self.length * p.x
            top = self.margin + self.length * (self.rows - p.y - 1)

            self.tile_ids[p] = self.create_image(left, top, image=self.sprites[name], anchor="nw")
        else:
            self.itemconfig(self.tile_ids[p], image=self.sprites[name])

    def get(self, p):
        return self.tile_names.get(p, None)

    def set_background(self, color):
        color = tuple(map(int, color))
        self.background_color = color
        bg_str = "#{:02X}{:02X}{:02X}".format(*color)
        self.itemconfig(self.background, fill=bg_str)

    def get_background(self):
        return self.background_color

    def remove(self, p):
        if p not in self.tile_names:
            return
        self.delete(self.tile_ids[p])
        del self.tile_ids[p]
        del self.tile_names[p]

    def clear(self):
        for i in range(self.cols):
            for j in range(self.rows):
                self.set(Point(i,j), None)