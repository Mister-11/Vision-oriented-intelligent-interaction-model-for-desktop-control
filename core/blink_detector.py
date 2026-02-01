import math
import time

def euclidean(p1, p2):
    return math.dist((p1.x, p1.y), (p2.x, p2.y))

class BlinkDetector:
    def __init__(self, settings=None):
        self.settings = settings
        # EAR (eye aspect ratio) threshold for blink detection
        self.ear_thresh = getattr(settings, "ear_thresh", 0.25) if settings else 0.25
        self.last_blink = 0
        self.blink_start = None

    def eye_aspect_ratio(self, landmarks, idxs):
        A = euclidean(landmarks[idxs[1]], landmarks[idxs[5]])
        B = euclidean(landmarks[idxs[2]], landmarks[idxs[4]])
        C = euclidean(landmarks[idxs[0]], landmarks[idxs[3]])
        return (A + B) / (2.0 * C)

    def detect(self, landmarks):
        # landmark indices for left and right eyes (MediaPipe FaceMesh)
        left_idxs = [33, 160, 158, 133, 153, 144]
        right_idxs = [362, 385, 387, 263, 373, 380]

        left_EAR = self.eye_aspect_ratio(landmarks, left_idxs)
        right_EAR = self.eye_aspect_ratio(landmarks, right_idxs)
        avg_EAR = (left_EAR + right_EAR) / 2.0

        blink = False
        wink_left, wink_right = False, False

        if avg_EAR < self.ear_thresh:
            if not self.blink_start:
                self.blink_start = time.time()
        else:
            if self.blink_start:
                duration = time.time() - self.blink_start
                blink = True
                self.last_blink = duration
                self.blink_start = None

        if left_EAR < self.ear_thresh and right_EAR >= self.ear_thresh:
            wink_left = True
        if right_EAR < self.ear_thresh and left_EAR >= self.ear_thresh:
            wink_right = True

        return {
            "blink": blink,
            "wink_left": wink_left,
            "wink_right": wink_right,
            "duration": self.last_blink,
        }
