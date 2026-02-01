import pyautogui

class GazeTracker:
    """
    Simple gaze-to-screen mapper using MediaPipe Face Mesh landmarks.
    Computes an approximate gaze point from the centers of the left and right eyes
    and maps normalized coords to screen pixels. Applies EMA smoothing.
    """

    # Common FaceMesh landmark indices for eye corners/top/bottom
    LEFT_EYE_IDS = [33, 133, 159, 145]   # outer, inner, top, bottom
    RIGHT_EYE_IDS = [362, 263, 386, 374] # outer, inner, top, bottom

    def __init__(self, settings=None):
        self.settings = settings
        self.screen_w, self.screen_h = pyautogui.size()
        self.last_x, self.last_y = self.screen_w // 2, self.screen_h // 2
        # default smoothing if settings not provided or missing
        self.alpha = getattr(settings, "ema_alpha", 0.3) if settings else 0.3

    def _eye_center(self, landmarks, idxs):
        xs = [landmarks[i].x for i in idxs]
        ys = [landmarks[i].y for i in idxs]
        return sum(xs) / len(xs), sum(ys) / len(ys)

    def track(self, landmarks):
        """
        landmarks: results.multi_face_landmarks[0].landmark
        Returns (x_px, y_px) screen coordinates.
        """
        try:
            lx, ly = self._eye_center(landmarks, self.LEFT_EYE_IDS)
            rx, ry = self._eye_center(landmarks, self.RIGHT_EYE_IDS)
            # average both eyes
            nx = (lx + rx) / 2.0
            ny = (ly + ry) / 2.0
        except Exception:
            # if anything goes wrong, keep previous
            return int(self.last_x), int(self.last_y)

        # clamp normalized values
        nx = min(max(nx, 0.0), 1.0)
        ny = min(max(ny, 0.0), 1.0)

        # map to screen
        x = nx * self.screen_w
        y = ny * self.screen_h

        # EMA smoothing
        a = self.alpha
        smoothed_x = a * x + (1 - a) * self.last_x
        smoothed_y = a * y + (1 - a) * self.last_y

        self.last_x, self.last_y = smoothed_x, smoothed_y
        return int(smoothed_x), int(smoothed_y)
