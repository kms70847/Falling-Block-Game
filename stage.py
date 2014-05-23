from Tkinter import Frame
from collections import defaultdict

class Stage(Frame):
    """Abstract base class for all the things that happen on the screen."""
    def __init__(self, parent):
        """
            parent should be a Tkinter widget capable of containing objects. Ex. a Tk() instance or Frame.
        """
        Frame.__init__(self, parent)
        self.parent = parent
        self.callback_ids = defaultdict(set)

        #coroutines are yielding functions which are intended to be run over the course of several frames.
        #all coroutines must have at least one yield statement in them.
        self.coroutines = []

    def start(self):
        """
            kicks off the idle callback
        """
        self.__idle()

    def __idle(self):
        """
            private method that repeatedly invokes each coroutine and self.idle
        """
        for coroutine in self.coroutines[:]:
            try:
                next(coroutine)
            except StopIteration:
                self.coroutines.remove(coroutine)
        self.idle()
        self.after(1000/120, self.__idle)
        #hopefully this terminates after `destroy` is invoked

    def bind_parent(self, event, callback):
        """
            binds a callback to the parent widget.
            the binding will be undone when `destroy` is invoked on this object.
        """
        func_id = self.parent.bind(event, callback, "+")
        self.callback_ids[event].add(func_id)

    def idle(self):
        """
            called whenever the parent isn't busy
        """
        pass
    def destroy(self):
        for event, ids in self.callback_ids.iteritems():
            for id in ids:
                self.parent.unbind(event, id)
        Frame.destroy(self)

    def replace(self, stage_class, *args, **kargs):
        """
            replace this existing stage with an instance of the given class.
            `self.parent`, *args and **kargs will be passed into its constructor.
        """
        self.destroy()
        s = stage_class(self.parent, *args, **kargs)
        s.pack()
        s.start()