import Tkinter

#extra label. Basically just a Label with a built in stringvar
class ExLabel(Tkinter.Label):
    def __init__(self, *args, **kargs):
        self.var = Tkinter.StringVar()
        kargs["textvar"] = self.var
        Tkinter.Label.__init__(self, *args, **kargs)
    def get(self):
        return self.var.get()
    def set(self, value):
        self.var.set(value)