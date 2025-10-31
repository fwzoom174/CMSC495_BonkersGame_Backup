import pygame
import os
import time

# Timer class for both stopwatch and countdown modes
class Timer:
    def __init__(self, screen, mode="stopwatch", countdown_time=60):
        """
        :param screen: the main pygame display surface
        :param mode: "stopwatch" or "countdown"
        :param countdown_time: starting time (seconds) for countdown mode
        """
        self.screen = screen
        self.mode = mode
        self.countdown_time = countdown_time
        self.start_time = None
        self.elapsed_time = 0
        self.paused = True
        self.font = self.load_custom_font(28)
        self.text_color = (255, 255, 255)

    # ---------- Font ----------
    def load_custom_font(self, size):
        font_path = os.path.join('media', 'graphics', 'font', 'Pixeboy.ttf')
        return pygame.font.Font(font_path, size)

    # ---------- Controls ----------
    def start(self):
        """Start the timer."""
        self.paused = False
        self.start_time = time.time()

    def pause(self):
        """Pause the timer."""
        if not self.paused:
            self.paused = True
            self.elapsed_time += time.time() - self.start_time

    def resume(self):
        """Resume after pause."""
        if self.paused:
            self.paused = False
            self.start_time = time.time()

    def reset(self):
        """Reset timer to zero or countdown start."""
        self.start_time = None
        self.elapsed_time = 0
        self.paused = True

    # ---------- Time Calculation ----------
    def get_time(self):
        """Return the current time value depending on mode."""
        if self.mode == "stopwatch":
            total = self.elapsed_time
            if not self.paused:
                total += time.time() - self.start_time
            return total
        else:  # countdown
            total = self.countdown_time - self.elapsed_time
            if not self.paused:
                total -= (time.time() - self.start_time)
            return max(total, 0)

    def update(self):
        """Update internal time and stop at zero for countdown mode."""
        if self.mode == "countdown" and not self.paused:
            remaining = self.get_time()
            if remaining <= 0:
                self.pause()
                # Added this part so the countdown can end the game when time runs out
                import scenes.breakout as breakout
                breakout.running = False  # game stops when timer hits zero

    # ---------- Draw ----------
    def draw(self):
        """Draw timer in the top-right corner of the screen."""
        seconds = int(self.get_time())
        minutes = seconds // 60
        seconds = seconds % 60

        time_text = f"{minutes:02}:{seconds:02}"
        text_surface = self.font.render(time_text, True, self.text_color)

        # Changed position to top-right corner (keeps it clear of scoreboard)
        text_rect = text_surface.get_rect(topright=(1180, 10))
        self.screen.blit(text_surface, text_rect)
