from stage import Stage
from Tkinter import *
from grid import Grid
from state import State, Request, Message
from geometry import Point
from fpsCounter import FpsCounter
from exLabel import ExLabel
from highScoreScreen import HighScoreScreen
import sound

#background colors, keyed by what level you must reach before they appear
level_colors = {
     0: (0xFF, 0xDB, 0x58), #mustard yellow
     5: (0xDD, 0x55, 0xCF), #violet
    10: (0x71, 0xEE, 0xB8), #seafoam green
    15: (0x27, 0x85, 0x24), #pine green
    20: (0xCC, 0xCC, 0xCC), #light gray
    25: (0x00, 0x00, 0x00), #black
    30: (0x00, 0x66, 0xCC)  #navy blue
}

def get_color(piece):
    """
        get the color associated with a particular piece
    """
    colors = {
        "I": "cyan",
        "J": "blue",
        "L": "orange",
        "O": "yellow",
        "S": "green",
        "T": "violet",
        "Z": "red"
    }
    return colors[piece.name]


class GameDisplay(Stage):
    def __init__(self, parent, state):
        Stage.__init__(self, parent)
        self.state = state
        
        self.state = state
        
        self.fps_counter = FpsCounter()

        self.init_widgets()
        self.init_bindings()

        self.ghost_piece = None

        #True when the user pauses the game
        self.paused = False

        #True when a coroutine is playing that should halt game logic, ex. when lines flash before disappearing
        self.blocking = False

        self.state.register_listener(self.model_alert)
        self.state.start()
        self.update_labels()

    def init_widgets(self):
        rows = self.state.rows - self.state.obstructed_rows
        self.field = Grid(self, rows=rows, cols=self.state.cols, length=25, background_color = level_colors[0])
        self.field.grid(row=0,column=0)

        info = Frame(self)
        info.grid(row=0, column=1)

        Label(info, text="Hold").pack()
        self.hold = Grid(info, rows=4, cols=4, length=25)
        self.hold.pack()

        Label(info, text="Preview").pack()
        self.preview = Grid(info, rows=4, cols=4, length=25)
        self.preview.pack()

        self.level_label = ExLabel(info)
        self.level_label.pack()

        self.line_label = ExLabel(info)
        self.line_label.pack()

        self.score_label = ExLabel(info)
        self.score_label.pack()

        self.fps_label = ExLabel(info)
        self.fps_label.pack()

    def init_bindings(self):
        self.bind_parent("<Down>", lambda *event: self.send(Request.down))
        self.bind_parent("<Left>", lambda *event: self.send(Request.left))
        self.bind_parent("<Right>", lambda *event: self.send(Request.right))
        self.bind_parent("<Return>", lambda *event: self.send(Request.hard_drop))
        self.bind_parent("<space>", lambda *event: self.send(Request.rotate_left))
        self.bind_parent("<z>", lambda *event: self.send(Request.rotate_left))
        self.bind_parent("<Up>", lambda *event: self.send(Request.hold))
        self.bind_parent("<x>", lambda *event: self.send(Request.rotate_right))
        self.bind_parent("<p>", lambda *event: self.toggle_paused())
        self.bind_parent("<c>", lambda *event: self.send(Request.up))
        
    def toggle_paused(self):
        self.paused = not self.paused
        if self.paused:
            sound.pause_music()
        else:
            sound.resume_music()
        sound.play("pause")

    def update_labels(self):
        self.score_label.set("Score: " + str(self.state.score))
        self.line_label.set("Lines: " + str(self.state.lines_cleared))
        self.level_label.set("Level: " + str(self.state.level))

    def send(self, msg):
        if not self.paused and not self.blocking:
            self.state.consume_message(msg)

    def idle(self):
        self.fps_counter.tick()
        self.fps_label.set("FPS: " + str(self.fps_counter.fps))
        if not self.blocking:
            self.send(Request.idle)

    def model_alert(self, message):
        """
            callback function for messages from the game state.
        """
        def set(piece, color, grid=self.field):
            for p in piece:
                grid.set(p, color)
        def update_ghost_piece():
            #erase the last frame's ghost piece
            if self.ghost_piece:
                set(self.ghost_piece, None)
            
            self.ghost_piece = self.state.get_ghost_piece()
            for p in self.ghost_piece:
                #determine which edges should be drawn.
                #don't draw edges that have a neighbor in that direction
                d = {Point(0,1): "U", Point(0,-1): "D", Point(1,0): "R", Point(-1,0): "L"}
                edges = "".join(sorted(letter for dir, letter in d.iteritems() if p + dir not in self.ghost_piece))
                self.field.set(p, "ghost/{}_{}".format(edges, get_color(self.ghost_piece)))
            self.ghost_piece = self.state.get_ghost_piece()
        if message.type == "PieceLocked":
            set(message.piece, get_color(message.piece))
            sound.play("lock_in")
            self.ghost_piece = None
        elif message.type == "PieceAppeared":
            #defer drawing the ghost piece if a coroutine is executing
            if not self.blocking:
                update_ghost_piece()
            set(message.piece, get_color(message.piece))
            self.preview.clear()
            p = self.state.queue.peek()
            set(p, get_color(p), self.preview)
        elif message.type == "PieceRotated":
            sound.play("rotate")
            update_ghost_piece()
            set(message.old, None)
            set(message.new, get_color(message.new))
        elif message.type == "PieceMoved":
            update_ghost_piece()
            set(message.old, None)
            set(message.new, get_color(message.new))
        elif message.type == "PieceHeld":
            set(message.old_piece, None)
            if message.old_held:
                set(message.old_held, None, self.hold)
            set(message.new_held, get_color(message.new_held), self.hold)
        elif message.type == "RowsCleared":
            #this logic needs to be a coroutine since we want to play a multiple-frame animation
            def iter_cleared_blocks():
                for i in range(self.state.cols):
                    for j in message.removed:
                        yield Point(i,j)
            def clearRows():
                #fancy flashing animation
                colors = {p: self.field.get(p) for p in iter_cleared_blocks()}
                #make sure this constant is odd so the blocks finish off as white
                blinks = 2
                frames_per_blink = 2
                for frame in range(blinks * 2 + 1):
                    for p in iter_cleared_blocks():
                        color = None if frame % 2 == 0 else colors[p]
                        self.field.set(p, color)
                    for i in range(frames_per_blink):
                        yield
                #remove the blocks for real
                #move lower blocks before higher ones, or else you might transpose new blocks to the wrong place
                for old_pos, new_pos in sorted(message.moved.iteritems(), key=lambda (a,b): (a.y, a.x)):
                    self.field.set(new_pos, self.field.get(old_pos))
                    self.field.set(old_pos, None)
                update_ghost_piece()
                self.blocking = False
            sound.play("line_clear")
            self.blocking = True
            self.coroutines.append(clearRows())
        elif message.type == "ScoreIncreased":
            self.update_labels()
        elif message.type == "LinesClearedIncreased":
            self.update_labels()
        elif message.type == "LevelIncreased":
            def background_transition(old, new):
                a = Point(*old)
                b = Point(*new)
                frames = 16
                for i in range(1, frames+1):
                    frac = float(i) / frames
                    m = a*(1-frac) + b*frac
                    self.field.set_background(m.tuple())
                    yield
            self.update_labels()
            print message.new
            if message.new in level_colors:
                old = self.field.get_background()
                new = level_colors[message.new]
                print old, new
                self.coroutines.append(background_transition(old, new))
        elif message.type == "GameLost":
            def loseGame():
                delay = 5
                changes_per_frame = 5
                changes_this_frame = 0
                for i in range(delay):
                    yield
                sound.pause_music()
                sound.play("game_lost")
                for j in range(self.state.rows - self.state.obstructed_rows):
                    for i in range(self.state.cols):
                        self.field.set(Point(i,j), "black")
                        changes_this_frame += 1
                        if changes_this_frame == changes_per_frame:
                            yield
                            changes_this_frame = 0
                for i in range(30):
                    yield
                self.replace(HighScoreScreen, self.state.score)
                
            self.blocking = True
            self.coroutines.append(loseGame())
        else:
            print "no handler yet for event " + message.type