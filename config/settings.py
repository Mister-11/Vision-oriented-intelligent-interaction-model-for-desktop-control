class Settings:
    def _init_(self):
        # EAR threshold for blink detection
        self.ear_thresh = 0.22
        # Frames required to count blink
        self.ear_frames = 3
        # Long blink time (seconds) → drag/drop
        self.long_blink_secs = 0.8
        # Exponential moving average alpha (smoothing)
        self.ema_alpha = 0.35
        # Scroll zone size
        self.scroll_band = 80
        # Dwell click
        self.dwell_secs = 1.5
        self.dwell_radius_px = 40