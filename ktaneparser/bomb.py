import threading, time

STRIKE_TIME_FACTORS = {
    0:  1 / 1,
    1:  1 / 1.25,
    2:  1 / 1.5,
    3:  1 / 1  # this is here because my program will crash so whatever
}

class Bomb:

    def __init__(self):
        self.seed = 0
        self.modules_remaining = []
        self.modules_solved = []
        self.max_strikes = 0
        self.strikes = 0
        self.time = 0
        self.bomb_running = False

    def start_bomb(self):
        print "Starting bomb"
        self.time -= 1 #do the first tick because we're late
        self.bomb_running = True
        # init timer shit here
        timer = threading.Timer(1, self._tick)
        timer.start()


    def _tick(self):
        self.time -= 1
        print self.time
        if self.time < 0:
            self.bomb_running = False
        if self.bomb_running:
            timer = threading.Timer(STRIKE_TIME_FACTORS[self.strikes], self._tick)
            timer.start()

    def stop_bomb(self):
        print "Stopping bomb"
        self.bomb_running = False

    def get_formatted_time(self):
        return "%d:%02d" % (self.time / 60, self.time % 60)

if __name__ == '__main__':
    print "init"
    b = Bomb()
    b.time = 60
    b.start_bomb()
    time.sleep(10)
    b.stop_bomb()