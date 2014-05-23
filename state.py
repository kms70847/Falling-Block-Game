from polyomino import make_polyomino
from geometry import Point
from collections import deque
from broadcaster import Broadcaster
from event import *

import random
def gen_bags():
    polyominos = map(make_polyomino, "ITJLSZO")
    while True:
        random.shuffle(polyominos)
        for piece in polyominos:
            yield piece.copy()

#piece generator that only makes line pieces.
#useful for debugging.
def gen_line_pieces():
    i = make_polyomino("I")
    while True:
        yield i.copy()

class PieceQueue:
    """
        class which provides an infinite stream of polynomials, and allows you to peek at the next N pieces.
        initializer requires a generator that perpetually yields pieces.
    """
    def __init__(self, generate):
        self.generator = generate()
        self.pending = deque()
    def peek(self, N=0):
        """
            returns the pieces that will be returned by `get`.
            N=0 returns the very next piece, N=1 returns the one that comes after that, etc.
        """
        #it would be nice if this were constant time rather than linear :-(

        #pull items from the generator until we get the queried one.
        while len(self.pending) <= N:
            self.pending.append(next(self.generator))
        return self.pending[N]
    def next(self):
        if self.pending:
            return self.pending.popleft()
        else:
            return next(self.generator)

class Request:
    """
        requests that may be sent by the controller to the State
    """
    hard_drop = 0
    left = 1
    right = 2
    down = 3
    up = 4 #available in debug mode only :3
    rotate_right = 5
    rotate_left = 6
    idle = 8 #do nothing
    hold = 9

class Message:
    """
        messages that may be sent by the state to the controller
    """
    game_lost = 0
    piece_moved = 1
    piece_rotated = 2
    piece_locked = 3
    row_cleared = 4
    level_increased = 5
    score_increased = 6

#reminder: rows are numbered with 0 being lowest.
#so pieces spawn on a high-numbered row and gradually travel to lower ones.
class State(Broadcaster):
    def __init__(self, **kargs):
        Broadcaster.__init__(self)
        self.queue = PieceQueue(kargs.get("generator", gen_bags))
        #self.queue = PieceQueue(kargs.get("generator", gen_line_pieces))
        self.queue.peek()

        self.cols = kargs.get("cols", 10)
        self.rows = kargs.get("rows", 22) #typically 16 to 24. 22 is recommended.
        self.obstructed_rows = 2
        self.blocks = set()

        self.score = 0
        self.lines_cleared = 0
        self.level = 0

        self.frames_since_last_drop = 0
        self.frames_between_drops = self.get_frames_between_drops()

        self.held_piece = None
        self.may_hold = True
        self.active_piece = None

        self.lost = False
    
    #we don't want to do anything that raises an event, until after listeners get a chance to register.
    #so the client should create this object, register its listeners, and then call start.
    def start(self):
        self.generate_active_piece(self.queue.next())
    def generate_active_piece(self, piece=None):
        """put the given piece on the top of the field."""
        self.current_piece = piece

        #where a piece spawns depends on the piece's width.
        left = min(p.x for p in self.current_piece)
        right = max(p.x for p in self.current_piece)

        width = right - left + 1

        #pieces with an even width should spawn centered on the field.
        if width % 2 == 0:
            x = self.cols/2 - width/2
        #pieces with an odd width should spawn slightly left of center.
        else:
            x = self.cols/2 - (width-1)/2 - 1
        
        #pieces should spawn as high as possible in the visible zone.
        y = self.rows - 2 - self.obstructed_rows
        self.current_piece.move_to(Point(x,y))

        self.notify(PieceAppeared(self.current_piece.copy()))
        if not self.is_valid_placement(self.current_piece):
            self.notify(GameLost())
            self.lost = True

    def lock_piece(self):
        """locks the active piece into its current position"""
        for p in self.current_piece:
            self.blocks.add(p)
        self.notify(PieceLocked(self.current_piece.copy()))
        self.check_rows()
        #todo: trigger game loss if this piece lies completely in the obstructed zone
        self.generate_active_piece(self.queue.next())
        self.may_hold = True
    def apply_gravity(self):
        """
            pulls down the current piece, locking it if necessary.
        """
        cand = self.current_piece.copy()
        cand.move(Point(0,-1))
        if self.is_valid_placement(cand):
            old = self.current_piece.copy()
            self.current_piece = cand
            new = self.current_piece.copy()
            self.notify(PieceMoved(old, new))
        else:
            self.lock_piece()
        self.frames_since_last_drop = 0
    def get_frames_between_drops(self):
        d = {
            0: 53,
            1: 49,
            2: 45,
            3: 41,
            4: 37,
            5: 33,
            6: 28,
            7: 22,
            8: 17,
            9: 11,
            10: 10,
            11: 9,
            12: 8,
            13: 7,
            14: 6,
            15: 6,
            16: 5,
            17: 5,
            18: 4,
            19: 4,
            20: 3
        }
        #return d[self.level]
        #adjust for our poor frame rate.
        return int(d[self.level] * 45.0 / 60.0)
            
    def check_rows(self):
        """
            determine if any rows need to be cleared.
            returns a list of rows cleared.
        """

        def clear(row):
            """
                removes all blocks from the given row, and moves down by one space all blocks above that row.
            """
            for i in range(self.cols):
                self.blocks.remove(Point(i,row))
            for j in range(row+1, self.rows):
                for i in range(self.cols):
                    target = Point(i,j)
                    destination = Point(i,j-1)
                    if target in self.blocks:
                        self.blocks.remove(target)
                        self.blocks.add(destination)

        rows_to_clear = []
        #possible enchancement: only check the rows of the last current piece when it locked in.
        for j in range(self.rows):
            if all(Point(i,j) in self.blocks for i in range(self.cols)):
                rows_to_clear.append(j)

        if rows_to_clear:

            moved_blocks = {}
            for p in self.blocks:
                if p.y in rows_to_clear: continue
                dy = len([row for row in rows_to_clear if row <= p.y])
                if dy > 0:
                    moved_blocks[p] = p + Point(0,-dy)

            #start from the top, moving down, or else `row` will be off by one in the second iteration
            for row in reversed(rows_to_clear):
                clear(row)

            self.notify(RowsCleared(
                rows_to_clear[:], 
                moved_blocks
            ))

            self.lines_cleared += len(rows_to_clear)
            self.notify(LinesClearedIncreased())

            self.score += {1:40, 2:100, 3:300, 4:1200}[len(rows_to_clear)] * (self.level+1)
            self.notify(ScoreIncreased())

            #bit of overkill to use while here instead of if,
            #but what if we want to support eleven unit tall line pieces?
            #then you could gain two levels with one move.
            while self.lines_cleared / 10 > self.level:
                self.level += 1
                self.notify(LevelIncreased(self.level-1, self.level))
                self.frames_between_drops = self.get_frames_between_drops()
        return rows_to_clear
    def get_ghost_piece(self):
        """
            updates the position of the ghost piece.
            The ghost piece is where the current piece will be locked in if the user does a hard drop.
        """
        cand = self.current_piece.copy()
        while True:
            cand.move(Point(0,-1))
            if not self.is_valid_placement(cand):
                cand.move(Point(0,1))
                break
        return cand
    def is_valid_placement(self, cand):
        """returns True if the candidate block can be placed in the field, False otherwise"""
        #out of bounds
        if any(p.y < 0 or p.y >= self.rows or p.x < 0 or p.x >= self.cols for p in cand):
            return False
        #overlaps an existing block
        if self.blocks.intersection(cand):
            return False
        return True
    def consume_message(self, msg):
        if self.lost:
            return
        #do nothing. Sent regularly by the view.
        #(60 per second would be nice)
        if msg == Request.idle:
            self.frames_since_last_drop += 1
            if self.frames_since_last_drop == self.frames_between_drops:
                self.apply_gravity()
        #move piece left or right or up, if possible
        elif msg in (Request.left, Request.right, Request.up):
            cand = self.current_piece.copy()
            delta = Point(0,0)
            if msg == Request.left: delta.x -= 1
            elif msg == Request.right: delta.x += 1
            elif msg == Request.up: delta.y += 1
            else: raise Exception("unexpected message")
            cand.move(delta)
            if self.is_valid_placement(cand):
                old = self.current_piece.copy()
                self.current_piece = cand.copy()
                new = self.current_piece.copy()
                self.notify(PieceMoved(old, new))
        #rotate piece, if possible.
        elif msg in (Request.rotate_left, Request.rotate_right):
            cand = self.current_piece.copy()
            if msg == Request.rotate_left: cand.rotate_left()
            else: cand.rotate_right()
            if self.is_valid_placement(cand):
                old = self.current_piece.copy()
                self.current_piece = cand.copy()
                new = self.current_piece.copy()
                self.notify(PieceRotated(old, new))
            #todo: implement "slide under" rotation.
        elif msg == Request.down:
            self.apply_gravity()
        elif msg == Request.hard_drop:
            old = self.current_piece.copy()
            self.current_piece = self.get_ghost_piece()
            new = self.current_piece.copy()
            if old != new:
                self.notify(PieceMoved(old, new))
                #user should get a constant amount of frames to readjust before lock-in.
                #this might actually increase the drop timer, but I guess that's OK.
                #(maybe this constant should scale down as level increases?)
                self.frames_since_last_drop = self.frames_between_drops - 10
        elif msg == Request.hold:
            if self.may_hold:
                if self.held_piece == None:
                    next = self.queue.next()
                else:
                    next = self.held_piece
                old_piece = self.current_piece.copy()
                old_held = None if not self.held_piece else self.held_piece.copy()
                self.held_piece = self.current_piece
                self.held_piece.reset()
                new_held = self.held_piece.copy()
                self.notify(PieceHeld(old_piece, old_held, new_held))
                self.may_hold = False
                self.generate_active_piece(next)
        else:
            raise Exception("didn't recognize message!")