from Tkinter import *
from stage import Stage
from state import State

import titleScreen

import pickle

hs_file = "high_scores.txt"

class Score:
    def __init__(self, name, points):
        self.name = name
        self.points = points

class HighScores:
    def __init__(self, **kargs):
        self.scores = []
        self.max_size = kargs.get("max_size", 10)
    def add(self, score):
        idx = self.potential_position(score)
        if idx != None:
            self.scores.insert(idx, score)
        if len(self.scores) > self.max_size:
            self.scores = self.scores[:self.max_size]
    def get(self, idx):
        if idx >= len(self.scores):
            return None
        else:   
            return self.scores[idx]
    def potential_position(self, score):
        """
            returns the index that the given score would have if inserted into the list.
            returns None if the score is not high enough.
        """
        for idx, cur_score in enumerate(self.scores):
            if score.points >= cur_score.points:
                return idx

        #score didn't beat any existing ones,
        #but we may have room to add it to the end
        if len(self.scores) >= self.max_size:
            return None
        else:
            return len(self.scores)        

def load_high_scores():
    try:
        with open(hs_file) as file:
            return pickle.load(file)
    except IOError:
        return HighScores()

def save_high_scores(data):
    with open(hs_file, "w") as file:
        pickle.dump(data, file)

class HighScoreScreen(Stage):
    def __init__(self, parent, score_to_add = None):
        Stage.__init__(self, parent)

        self.score_to_add = score_to_add
        self.high_scores = load_high_scores()

        self.new_idx = None
        if self.score_to_add != None:
            s = Score("???", self.score_to_add)
            self.new_idx = self.high_scores.potential_position(s)
        if self.new_idx != None:
            self.high_scores.add(s)

        score_frame = Frame(self)
        score_frame.pack()
        for i in range(self.high_scores.max_size):
            score = self.high_scores.get(i)
            if score != None:
                score = self.high_scores.scores[i]
                name = score.name
                points = str(score.points)
            else:
                name = "---"
                points = "---"                
            if i == self.new_idx:
                self.new_entry = Entry(score_frame)
                self.new_entry.grid(row=i, column=0)
            else:
                Label(score_frame, text=name).grid(row=i,column=0)
            Label(score_frame, text=points).grid(row=i,column=1)

        b = Button(self, text="return to main", command=self.button_clicked)
        b.pack()
        
    def button_clicked(self):
        if self.new_idx != None:
            self.high_scores.scores[self.new_idx].name = self.new_entry.get()
            save_high_scores(self.high_scores)
        self.replace(titleScreen.TitleScreen)
        