import time

class FpsCounter:
    def __init__(self):
        self.fps = 0
        self.ticks = 0
        self.start_time = time.time()
    def tick(self):
        self.ticks += 1
        if self.ticks == 60:
            self.ticks = 0
            cur_time = time.time()
            dif = cur_time - self.start_time
            self.fps = 60 / dif
            self.start_time = cur_time
        