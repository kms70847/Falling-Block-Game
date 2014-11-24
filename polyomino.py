from geometry import Point

class Polyomino:
    def __init__(self):
        self.delta = Point(0,0)
        self.orientation = 0
        self.points = [[],[],[],[]]
        self.name = ""
    def __iter__(self):
        for point in self.points[self.orientation]:
            yield point + self.delta
    def rotate_right(self):
        self.orientation = (self.orientation+1)%4
    def rotate_left(self):
        self.orientation = (self.orientation-1)%4
    def move(self, delta):
        self.delta += delta
    def move_to(self, target):
        """moves such that the top left corner of the Polyomino's hitbox is at target."""
        left = min(p.x for p in self)
        top  = min(p.y for p in self)
        dx = target.x - left
        dy = target.y - top
        self.move(Point(dx,dy))
    def reset(self):
        self.delta = Point(0,0)
        self.orientation = 0
    def copy(self):
        ret = Polyomino()
        ret.delta = self.delta.copy()
        ret.orientation = self.orientation
        ret.name = self.name
        for i in range(4):
            ret.points[i] = map(Point.copy, self.points[i])
        return ret
    def __eq__(self, other):
        if not isinstance(other, Polyomino):
            return False
        return set(self) == set(other)
    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "Polyomino({})".format(", ".join(map(str, self)))

def make_polyomino(letter):
    """
    factory function that makes polyominos based on a single character.
    valid characters: I J L O S T Z
    """
    with open("pieces/{}.txt".format(letter.upper())) as file:
        data = file.read().replace("\r", "")
        frames = data.split("\n\n")
        assert len(frames) == 4, "expected exactly four orientation frames"
        p = Polyomino()
        for idx, frame in enumerate(frames):
            rows = frame.split("\n")
            assert len(rows) == 4, "expected exactly four rows in frame {}".format(idx)
            assert all(len(row) == 4 for row in rows), "expected exactly four columns in frame {}".format(idx)
            for i in range(4):
                for j in range(4):
                    if rows[3-j][i] == "x":
                        p.points[idx].append(Point(i,j))
        p.name = letter
        return p
