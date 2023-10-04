import time

class MeasureDuration:

    def __init__(self,label = '',autostart=True):
        self.label              = label
        self._is_running        = False
        self._start             = 0.0
        self._stop              = 0.0
        self._previous_duration = 0.0
        if autostart:
            self.start()
        

    def start(self):
        if not self._is_running:
            self._start = time.time()
            self._stop = 0
            self._is_running = True
    
    def stop(self):
        if  self._is_running and self._start > 0:
            self._stop = time.time()
            self._previous_duration = self._previous_duration + (self._stop - self._start)
            self._is_running = False

    @property
    def duration_seconds(self):
        if self._is_running:
            return self._previous_duration + (time.time() - self._start)
        return self._previous_duration

class MeasureProgress(MeasureDuration):

    def __init__(self,total=0,label='',autostart=True):
        super().__init__(label=label,autostart=autostart)
        self.total = total
        self.done = 0

    def stop(self,is_ready=True):
        super().stop()
        if is_ready:
            self.done = self.total
    
    @property
    def average_speed_nr_per_sec(self):
        duration = self.duration_seconds
        if duration > 0:
            return self.done / duration
        else:
            return -1 

    @property
    def done_percentage(self):
        if self.total > 0:
            return (self.done / self.total) * 100
        else:
            return 0.0

    @property
    def todo(self):
        return self.total - self.done

    @property
    def remaining_estimate_sec(self):
        speed = self.average_speed_nr_per_sec
        if speed > 0:
            return self.todo / self.average_speed_nr_per_sec
        else:
            return -1
