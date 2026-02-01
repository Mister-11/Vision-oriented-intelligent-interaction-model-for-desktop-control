This project allows controlling the computer mouse *using eyes only*.  
It combines *OpenCV, **MediaPipe, and **PyAutoGUI* to track eye movements, detect blinks/winks, and map gaze to cursor movements.  
Designed as an *HCI (Human-Computer Interaction) system* for accessibility.

---

## 🚀 Features
- Real-time *cursor movement* with iris tracking
- *Blink & wink gestures*:
  - Left wink → Left click
  - Right wink → Right click
  - Double blink → Double click
  - Long blink → Drag & drop
- *Smooth cursor movement* (Exponential Moving Average)
- *Dwell-to-click* (stare at one point to auto-click)
- *Auto-scroll* by looking at top/bottom of the screen
- *4-point calibration* for accuracy
- On-screen overlays for debugging
- Extendable with *voice commands* or *GUI settings panel*

---

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/EyeControlledMouse.git
   cd EyeControlledMouse