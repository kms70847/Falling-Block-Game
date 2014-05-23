from PIL import Image, ImageDraw
from geometry import Point

def mid(a,b, frac):
    return a*(1-frac) + b*frac

def mid_color(a, b, frac):
    return tuple(int(mid(x,y, frac)) for x,y in zip(a,b))

black = (0,0,0)
white = (255,255,255)

def create_image(color, right, down, left, up):
    #the grid cell size is 25*25, but we want a little bleed over
    #for the black outline
    width = 26
    height =26

    margin = 4

    im = Image.new("RGBA", (width, height))

    draw = ImageDraw.Draw(im)

    #each corner of the square, starting in the upper-left and moving clockwise
    a = Point(0,0)
    b = Point(width-1, 0)
    c = Point(width-1, height) - Point(0,1)
    d = Point(0, height) - Point(0,1)
    corners = [a,b,c,d]

    if up:    draw.line([a.tuple(), b.tuple()], fill=color)
    if right: draw.line([b.tuple(), c.tuple()], fill=color)
    if down:  draw.line([c.tuple(), d.tuple()], fill=color)
    if left:  draw.line([d.tuple(), a.tuple()], fill=color)

    return im

colors = {
    "cyan": (0,255,255),
    "blue": (0,0,255),
    "orange": (255,165,0),
    "yellow": (255,255,0),
    "green": (0,255,0),
    "violet": (143, 0, 255),
    "red": (255,0,0)
}

for right in (True, False):
    for down in (True, False):
        for left in (True, False):
            for up in (True, False):
                if all(not dir for dir in [right, down, left, up]): continue
                for name, color in colors.iteritems():
                    im = create_image(color, right, down, left, up)
                    dirs = ("R" if right else "") + ("D" if down else "") + ("L" if left else "") + ("U" if up else "")
                    dirs = "".join(sorted(dirs))
                    im.save("ghost/{}_{}.png".format(dirs, name))