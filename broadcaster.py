class Broadcaster:
    """
    Broadcaster class.
    allows other callables to register as listeners to it,
    and notifies them when something happens.
    """
    def __init__(self):
        self.listeners = []
    def register_listener(self, listener):
        self.listeners.append(listener)
    def notify(self, message):
        for listener in self.listeners:
            listener(message)