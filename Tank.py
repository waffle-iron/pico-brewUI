import time
from datetime import timedelta, datetime
from PID import PID

SAMPLE_HISTORY = 10

class List_max():

    def __init__(self, max_size):
        self.max_size = max_size
        self.array    = []


    def append(self, obj):
        if (len(self.array) >= self.max_size):
            self.array.pop(0)

        self.array.append(obj)

class Chrono():

    def __init__(self):
        self.start_chrono = None
        self.start_pause  = None



    def launch_chrono(self, duration):
        self.start_chrono = time.time()
        self.duration     = duration


    def is_over(self):
        if (self.start_pause is not None):
            return False
        elif(self.start_chrono is None):
            return True
        else:
            if (time.time() < self.start_chrono + self.duration):
                return False
            else:
                return True

    def pause(self):
        if (self.is_over()):
            return
        now              = time.time()
        self.start_pause = now
        self.lasting     = self.duration - (now - self.start_chrono)

    def resume(self):
        now = time.time()
        pause_duration = now - self.start_pause

        self.start_chrono += pause_duration

        self.start_pause = None # keep this line last !
        # do not write here !

    def lasting(self):
        if (self.start_pause is not None):
            return self.lasting
        now = time.time()
        return now - self.start_chrono


class Tank(PID, Chrono):

    def __init__(self):
        self.temperature_samples = []
        self.last_fill           = 0
        self.current_volume      = 0

        self.temperatures = List_max(SAMPLE_HISTORY)
        self.volumes      = List_max(SAMPLE_HISTORY)
        self.powers       = List_max(SAMPLE_HISTORY)
        self.timing       = List_max(SAMPLE_HISTORY)


        PID.__init__(self)
        Chrono.__init__(self)

    def update_pid(self, value):
        now  = time.time()
        nowd = datetime.now()
        if(now - self.last_fill > timedelta(minutes=5).seconds):
            self.last_fill = now
            self.temperatures.append(value)
            self.timing.append(str(nowd.hour) + ":" + str(nowd.minute))
            self.volumes.append(self.current_volume)

        #compute pid
        self.update(value)
