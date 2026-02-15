import time

class FPSMonitor:
    def __init__(self):
        self.frame_count = 0
        self.previous_frame_time = 0
        self.frame_delays = []
        
    def tick(self):
        self.frame_count += 1
        frame_time = time.time()
        frame_delay = frame_time - self.previous_frame_time
        self.frame_delays.append(frame_delay)
        self.previous_frame_time = frame_time
    
    def get_fps(self):
        last_point = len(self.frame_delays)-1
        count = 0
        frame_counter = 0
        while count < 1:
            count += self.frame_delays[last_point]
            last_point -= 1
            frame_counter += 1
        return frame_counter