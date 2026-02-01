import pyautogui
import time
import math

class DwellClick:
    def __init__(self, settings=None):
        self.settings = settings
        self.last_pos = None
        self.start_time = None
        self.dwell_radius_px = getattr(settings, "dwell_radius_px", 30) if settings else 30
        self.dwell_secs = getattr(settings, "dwell_secs", 1.0) if settings else 1.0

    def handle(self, pos):
        if self.last_pos is None:
            self.last_pos = pos
            self.start_time = time.time()
            return

        dist = math.dist(pos, self.last_pos)
        if dist < self.dwell_radius_px:
            if time.time() - self.start_time > self.dwell_secs:
                pyautogui.click()
                self.start_time = time.time()
        else:
            self.last_pos = pos
            self.start_time = time.time()
