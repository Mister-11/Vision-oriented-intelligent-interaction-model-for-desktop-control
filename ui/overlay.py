import cv2

class Overlay:
    def draw(self, frame, landmarks, blink_info, pos):
        h, w, _ = frame.shape
        for id in [33, 133, 362, 263, 159, 145, 386, 374, 475]:
            x, y = int(landmarks[id].x * w), int(landmarks[id].y * h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        cv2.putText(frame, f"Blink: {blink_info['blink']}", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Cursor: {pos}", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
