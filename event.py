#event.py - events raised by the game state


class Event(object):
    pass

class PieceAppeared(Event):
    def __init__(self, piece):
        self.type = "PieceAppeared"
        self.piece = piece

class PieceMoved(Event):
    def __init__(self, old, new):
        self.type = "PieceMoved"
        self.old = old
        self.new = new

class PieceRotated(Event):
    def __init__(self, old, new):
        self.type = "PieceRotated"
        self.old = old
        self.new = new

class PieceLocked(Event):
    def __init__(self, piece):
        self.type = "PieceLocked"
        self.piece = piece

class PieceHeld(Event):
    def __init__(self, old_piece, old_held, new_held):
        self.type = "PieceHeld"
        self.old_piece = old_piece
        self.old_held = old_held
        self.new_held = new_held

class RowsCleared(Event):
    def __init__(self, removed, moved):
        self.type = "RowsCleared"
        self.removed = removed
        self.moved = moved

class ScoreIncreased(Event):
    def __init__(self):
        self.type = "ScoreIncreased"

class LevelIncreased(Event):
    def __init__(self, old, new):
        self.type = "LevelIncreased"
        self.old = old
        self.new = new

class LinesClearedIncreased(Event):
    def __init__(self):
        self.type = "LinesClearedIncreased"

class GameLost(Event):
    def __init__(self):
        self.type = "GameLost"