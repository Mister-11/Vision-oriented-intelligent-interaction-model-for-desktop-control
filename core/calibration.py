import pyautogui

class Calibration:
    def __init__(self, settings=None):
        self.settings = settings
        self.points = []
        self.screen_w, self.screen_h = pyautogui.size()
        self.calibrated = False

    def add_point(self):
        # Save a calibration point (currently just full screen size)
        self.points.append((self.screen_w, self.screen_h))
        if len(self.points) >= 4:
            self.calibrated = True
