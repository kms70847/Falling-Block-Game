#prototype title screen.
#todo: make this a Stage subclass

from Tkinter import *
from stage import Stage
from state import State
import gameDisplay
import highScoreScreen
import sys
import sound

class Triangle(Canvas):
    def __init__(self, root, size):
        Canvas.__init__(self, root, width=size, height=size)
        self.size = size
        self.id = None
        self.show()
    def hide(self):
        if self.id == None: return
        self.delete(self.id)
        self.id = None
    def show(self):
        if self.id != None: return
        self.id = self.create_polygon(0,0,0,self.size, self.size, self.size/2, fill="black")
    def set_visible(self, is_visible):
        if is_visible:
            self.show()
        else:
            self.hide()

class Selection(Frame):
    def __init__(self, root, text, *args, **kargs):
        Frame.__init__(self, root, *args, **kargs)
        self.text = text

        self.icon = Triangle(self, 20)
        self.icon.grid(row=0, column=0)
    
        self.label = Label(self,text=text)
        self.label.grid(row=0, column=1)

        self.set_selected(False)
        self.set_selected(True)
    def set_selected(self, selected):
        self.selected = selected
        self.icon.set_visible(selected)

class SelectionGroup(Frame):
    def __init__(self, root, *names, **kargs):
        Frame.__init__(self, root, **kargs)
        self.selections = []
        for name in names:
            s = Selection(self, name)
            s.set_selected(False)
            s.pack(anchor="w")
            self.selections.append(s)
        self.selected_id = 0
        self.selections[0].set_selected(True)
    def set_selection_id(self, id):
        assert id >=0 and id < len(self.selections)
        self.selections[self.selected_id].set_selected(False)
        self.selected_id = id
        self.selections[self.selected_id].set_selected(True)
        sound.play("rotate")
    def next_selection(self):
        self.set_selection_id((self.selected_id + 1) % len(self.selections))
    def previous_selection(self):
        self.set_selection_id((self.selected_id - 1) % len(self.selections))
    def get_selection(self):
        return self.selections[self.selected_id].text

class TitleScreen(Stage):
    def __init__(self, parent, *args, **kargs):
        Stage.__init__(self, parent, *args, **kargs)

        Label(self, text="FALLING BLOCK GAME", font=("Helvetica", 30)).pack()

        self.selections = SelectionGroup(self, "Start", "High Scores", "Exit")
        self.selections.pack()
        self.bind_parent("<Up>"  , lambda event: self.selections.previous_selection())
        self.bind_parent("<Down>", lambda event: self.selections.next_selection())
        self.bind_parent("<Return>", self.selection_chosen)

    def selection_chosen(self, event):
        text = self.selections.get_selection()
        if text == "Exit":
            sys.exit()
        elif text == "Start":
            self.replace(gameDisplay.GameDisplay, State())
        elif text == "High Scores":
            self.replace(highScoreScreen.HighScoreScreen)