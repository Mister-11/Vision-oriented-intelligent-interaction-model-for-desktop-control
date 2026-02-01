import pyautogui

class Scrolling:
    def __init__(self, settings=None):
        self.settings = settings
        # Default scroll step if not in settings
        self.scroll_step = getattr(settings, "scroll_step", 50) if settings else 50

    def handle(self, screen_pos):
        """
        screen_pos: (x, y) pixel coordinates of gaze
        Uses vertical position of gaze to scroll up/down.
        """
        if not screen_pos:
            return

        _, y = screen_pos
        screen_h = pyautogui.size()[1]

        # Scroll up if looking near the top
        if y < screen_h * 0.25:
            pyautogui.scroll(self.scroll_step)

        # Scroll down if looking near the bottom
        elif y > screen_h * 0.75:
            pyautogui.scroll(-self.scroll_step)
