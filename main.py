import importlib
import subprocess
import sys
import os
import webbrowser
import threading
import time
from pathlib import Path

# ---------- Try to ensure required modules are installed ----------
# (Optional auto-install; comment out if you don't want auto installs)
_module_map = {
    "cv2": "opencv-python",
    "pyautogui": "pyautogui",
    "numpy": "numpy",
    "speech_recognition": "SpeechRecognition",
    "keyboard": "keyboard",
    "pyaudio": "pyaudio",
}

for _mod, _pkg in _module_map.items():
    try:
        importlib.import_module(_mod)
    except Exception:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", _pkg])
        except Exception:
            # if installation fails, we'll allow the import to fail later with an error
            pass

# ---------- Imports ----------
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import keyboard
import speech_recognition as sr

# ---------- Globals ----------
screen_w, screen_h = pyautogui.size()
alpha = 0.2  # smoothing factor for mouse movement
smooth_x, smooth_y = 0, 0

# ---------- Helper functions (place above voice_listener) ----------

def type_text_into_focused_field(text, press_enter=False):
    """
    Type text into the currently focused field using pyautogui.write.
    press_enter: if True, press Enter after typing.
    """
    try:
        # small pause so user can react/focus target field
        time.sleep(0.12)
        pyautogui.write(text, interval=0.03)
        if press_enter:
            pyautogui.press("enter")
        print(f"⌨️ Typed: {text}{' (and Enter)' if press_enter else ''}")
    except Exception as e:
        print("⚠️ Typing failed:", e)

def shutdown_system():
    print("🛑 Shutting down the system now...")
    try:
        if sys.platform.startswith("win"):
            os.system("shutdown /s /t 0")
        elif sys.platform == "darwin":
            os.system("osascript -e 'tell app \"System Events\" to shut down'")
        elif sys.platform.startswith("linux"):
            os.system("shutdown -h now")
        else:
            print("❌ Shutdown not supported on this platform via this script.")
    except Exception as e:
        print("⚠️ Shutdown command failed:", e)

def minimize_window():
    print("🗕 Minimizing active window...")
    try:
        if sys.platform.startswith("win"):
            import ctypes
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            hwnd = user32.GetForegroundWindow()
            SW_MINIMIZE = 6
            user32.ShowWindow(hwnd, SW_MINIMIZE)
        else:
            pyautogui.hotkey('alt', 'space')
            time.sleep(0.05)
            pyautogui.press('n')
    except Exception as e:
        print("⚠️ Minimize failed:", e)
        try:
            pyautogui.hotkey('alt', 'space')
            time.sleep(0.05)
            pyautogui.press('n')
        except Exception as ex:
            print("⚠️ Fallback minimize failed:", ex)

def restore_window():
    print("🗖 Restoring active window...")
    try:
        if sys.platform.startswith("win"):
            import ctypes
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            hwnd = user32.GetForegroundWindow()
            SW_RESTORE = 9
            user32.ShowWindow(hwnd, SW_RESTORE)
        else:
            pyautogui.hotkey('alt', 'space')
            time.sleep(0.05)
            pyautogui.press('r')
    except Exception as e:
        print("⚠️ Restore failed:", e)
        try:
            pyautogui.hotkey('alt', 'space')
            time.sleep(0.05)
            pyautogui.press('r')
        except Exception as ex:
            print("⚠️ Fallback restore failed:", ex)

def close_tab_or_window(close_tab_only=True):
    try:
        if close_tab_only:
            if sys.platform == "darwin":
                pyautogui.hotkey('command', 'w')
            else:
                pyautogui.hotkey('ctrl', 'w')
            print("✖️ Closed tab (Ctrl/Cmd+W).")
        else:
            if sys.platform.startswith("win"):
                pyautogui.hotkey('alt', 'f4')
            else:
                if sys.platform == "darwin":
                    pyautogui.hotkey('command', 'q')
                else:
                    pyautogui.hotkey('alt', 'f4')
            print("✖️ Closed window.")
    except Exception as e:
        print("⚠️ Close failed:", e)

# ---------- Voice listener (threaded) ----------
def voice_listener():
    recognizer = sr.Recognizer()
    mic_list = sr.Microphone.list_microphone_names()
    print("🎤 Available microphones:")
    for i, name in enumerate(mic_list):
        print(f"  {i}: {name}")

    mic_index = 0
    try:
        mic = sr.Microphone(device_index=mic_index)
    except Exception as e:
        print("⚠️ Failed to access the microphone:", e)
        return

    # Predefined websites for quick open
    websites = {
        "cricbuzz": "https://www.cricbuzz.com",
        "youtube": "https://www.youtube.com",
        "espn": "https://www.espn.com",
        "bbc": "https://www.bbc.com",
        "w3schools": "https://www.w3schools.com",
        "medium": "https://www.medium.com",
        "twitter": "https://www.twitter.com",
        "github": "https://www.github.com"
    }

    def callback(recognizer, audio):
        try:
            command = recognizer.recognize_google(audio, language="en-US").lower().strip()
            print(f"🎤 Voice command heard: '{command}'")

            # ====================== TYPE COMMAND FEATURE ======================
            if command.startswith("type:") or command.startswith("type "):
                payload = command

                # Remove 'type:' or 'type '
                if payload.startswith("type:"):
                    payload = payload[len("type:"):].strip()
                elif payload.startswith("type "):
                    payload = payload[len("type "):].strip()

                # Detect ending "enter"
                press_enter = False
                if payload.endswith(" enter"):
                    press_enter = True
                    payload = payload[:-6].strip()

                # If there is payload, type it
                if payload:
                    type_text_into_focused_field(payload, press_enter)
                else:
                    print("⚠️ Nothing to type after 'type' command.")
                return
            # ===============================================================

            # --- Search / open website handling (existing) ---
            if command.startswith("search "):
                query_text = command.replace("search", "").strip()
                if " on " in query_text:
                    parts = query_text.split(" on ")
                    query = parts[0].strip()
                    site = parts[1].strip().replace(" ", "")
                    url = f"https://www.google.com/search?q={query.replace(' ', '+')}+site:{site}.com"
                    print(f"🌍 Searching '{query}' on {site}")
                else:
                    if query_text in websites:
                        url = websites[query_text]
                        print(f"🌍 Opening website -> {query_text}")
                    else:
                        url = f"https://www.google.com/search?q={query_text.replace(' ', '+')}"
                        print(f"🌍 Google search -> {query_text}")

                # open with chrome if registered, else default
                try:
                    webbrowser.open(url)
                except Exception as e:
                    print("⚠️ Failed to open browser:", e)
                return

            # --- New voice commands for system/window control ---
            if "shut down" in command or "shutdown" in command:
                shutdown_system()
                return

            if "minimize" in command or "minimise" in command:
                minimize_window()
                return

            if "restore" in command or "maximize" in command or "maximise" in command or "unminimize" in command:
                restore_window()
                return

            if "close tab" in command or "close this tab" in command:
                close_tab_or_window(close_tab_only=True)
                return

            if "close window" in command:
                close_tab_or_window(close_tab_only=False)
                return

            # generic 'close' -> prefer close tab
            if command == "close":
                close_tab_or_window(close_tab_only=True)
                return

            # Try open named website if single word
            if command in websites:
                try:
                    webbrowser.open(websites[command])
                except Exception as e:
                    print("⚠️ Failed to open website:", e)
                return

            print("🤔 Voice command not mapped to any action.")
        except sr.UnknownValueError:
            print("🤔 Could not understand audio. Speak clearly.")
        except sr.RequestError as e:
            print(f"❌ Speech Recognition service error: {e}")
        except Exception as e:
            print("⚠️ Voice callback error:", e)

    # Threaded listening loop
    def listen_loop():
        print("🎙️ Voice recognition thread starting...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        while True:
            try:
                with mic as source:
                    print("🎤 Listening for voice command...")
                    audio = recognizer.listen(source, timeout=6, phrase_time_limit=6)
                    callback(recognizer, audio)
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print("⚠️ Voice listening loop error:", e)
                time.sleep(1)

    t = threading.Thread(target=listen_loop, daemon=True)
    t.start()
    print("🎙️ Voice recognition thread started (daemon).")

# ---------- Start voice listener ----------
voice_listener()

# ---------- Eye / webcam control ----------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
BLINK_THRESHOLD = 0.30
LONG_BLINK_TIME = 0.8
VERY_LONG_BLINK_TIME = 2.0
DWELL_TIME = 1.5

def eye_aspect_ratio(landmarks, eye_indices):
    points = np.array([(landmarks[p].x, landmarks[p].y) for p in eye_indices])
    A = np.linalg.norm(points[1] - points[5])
    B = np.linalg.norm(points[2] - points[4])
    C = np.linalg.norm(points[0] - points[3])
    return (A + B) / (2.0 * C)

cap = cv2.VideoCapture(0)
print("👁️ Eye Controlled Mouse started. Press ESC anytime to quit.")
status_message = ""
closed_frames = {"left": 0, "right": 0}
blink_start = None
drag_mode = False
last_pos = None
pos_start_time = None

try:
    while True:
        if keyboard.is_pressed("esc"):
            print("Exiting Eye Controlled Mouse (ESC pressed)...")
            break

        ret, frame = cap.read()
        if not ret:
            print("⚠️ Camera frame not available.")
            time.sleep(0.1)
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            # use iris landmark for gaze approx
            iris = landmarks[468]
            target_x, target_y = int(iris.x * screen_w), int(iris.y * screen_h)
            smooth_x = int(alpha * target_x + (1 - alpha) * smooth_x)
            smooth_y = int(alpha * target_y + (1 - alpha) * smooth_y)
            pyautogui.moveTo(smooth_x, smooth_y, duration=0.01)

            left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
            right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
            left_closed = left_ear < BLINK_THRESHOLD
            right_closed = right_ear < BLINK_THRESHOLD
            both_closed = left_closed and right_closed

            # Winks for left/right clicks
            if left_closed and not right_closed:
                closed_frames["left"] += 1
            elif right_closed and not left_closed:
                closed_frames["right"] += 1

            if closed_frames["left"] >= 3:
                pyautogui.click(button="left")
                status_message = "LEFT CLICK ✅"
                closed_frames["left"] = 0
            if closed_frames["right"] >= 3:
                pyautogui.click(button="right")
                status_message = "RIGHT CLICK ✅"
                closed_frames["right"] = 0

            # Long blink
            if both_closed:
                if blink_start is None:
                    blink_start = time.time()
                else:
                    blink_duration = time.time() - blink_start
                    if blink_duration >= VERY_LONG_BLINK_TIME:
                        pyautogui.hotkey("alt", "f4")
                        status_message = "VERY LONG BLINK ✅ Closed Active Window"
                        blink_start = None
            else:
                if blink_start is not None:
                    blink_duration = time.time() - blink_start
                    if blink_duration < 0.4:
                        pyautogui.doubleClick()
                        status_message = "DOUBLE CLICK ✅"
                    elif blink_duration >= LONG_BLINK_TIME:
                        drag_mode = not drag_mode
                        if drag_mode:
                            pyautogui.mouseDown()
                            status_message = "DRAG START ✅"
                        else:
                            pyautogui.mouseUp()
                            status_message = "DRAG END ✅"
                    blink_start = None

            # Dwell-to-click
            current_pos = (smooth_x // 50, smooth_y // 50)
            if current_pos == last_pos:
                if pos_start_time and time.time() - pos_start_time > DWELL_TIME:
                    pyautogui.click()
                    status_message = "DWELL CLICK ✅"
                    pos_start_time = None
            else:
                last_pos = current_pos
                pos_start_time = time.time()

        if status_message:
            print(status_message)
            status_message = ""

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting (q pressed).")
            break

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Clean exit.")
