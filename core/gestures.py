import pyautogui
import time

class GestureController:
    def __init__(self, settings=None):
        self.settings = settings
        self.dragging = False
        self.last_blink_time = 0
        self.long_blink_secs = getattr(settings, "long_blink_secs", 0.8) if settings else 0.8

    def handle(self, blink_info):
        if blink_info["wink_left"]:
            pyautogui.click(button="left")
        elif blink_info["wink_right"]:
            pyautogui.click(button="right")

        if blink_info["blink"]:
            now = time.time()
            if now - self.last_blink_time < 0.4:
                pyautogui.doubleClick()
            else:
                if blink_info["duration"] > self.long_blink_secs:
                    if not self.dragging:
                        pyautogui.mouseDown()
                        self.dragging = True
                    else:
                        pyautogui.mouseUp()
                        self.dragging = False
            self.last_blink_time = now
