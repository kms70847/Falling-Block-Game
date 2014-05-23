from PIL import Image, ImageDraw
from geometry import Point

def mid(a,b, frac):
    return a*(1-frac) + b*frac

def mid_color(a, b, frac):
    return tuple(int(mid(x,y, frac)) for x,y in zip(a,b))

black = (0,0,0)
white = (255,255,255)

def create_image(color):
    #the grid cell size is 25*25, but we want a little bleed over
    #for the black outline
    width = 26
    height =26

    margin = 4

    im = Image.new("RGB", (width, height))

    draw = ImageDraw.Draw(im)

    #each corner of the square, starting in the upper-left and moving clockwise
    a = Point(0,0)
    b = Point(width-1, 0)
    c = Point(width-1, height)
    d = Point(0, height)

    #bounds of the interior square
    inner_left = margin
    inner_right = width-margin-1
    inner_top = margin
    inner_bottom = height-margin

    #points of the interior square
    e = Point(inner_left, inner_top)
    f = Point(inner_right, inner_top)
    g = Point(inner_right, inner_bottom)
    h = Point(inner_left, inner_bottom)

    #left and right bevels
    draw.rectangle([a.tuple(), c.tuple()], fill=mid_color(color,black,0.1))

    #interior square
    draw.rectangle([e.tuple(), g.tuple()], fill=color)

    #upper bevel
    draw.polygon([p.tuple() for p in [a,b,f,e]], fill=mid_color(color, white, 0.5))
    #lower bevel
    draw.polygon([p.tuple() for p in [h,g,c,d]], fill=mid_color(color, black, 0.5))

    #outline
    draw.rectangle([a.tuple(), (c-Point(0,1)).tuple()], outline=black, fill=None)
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

for name, color in colors.iteritems():
    im = create_image(color)
    im.save("{}.png".format(name))