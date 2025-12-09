"""
This file creates the Timer used in the game.
It supports stopwatch and countdown modes,
updates the time, and draws the timer on the screen.
"""

import pygame
import os
import time
import scenes.breakout as breakout
from common import ROOT_PATH


# ---------- TIMER CLASS ---------- #
class Timer:
    # ---------- SETUP ---------- #
    def __init__(self, screen, mode="stopwatch", countdown_time=60):
        self.screen = screen
        self.mode = mode
        self.countdown_time = countdown_time
        self.start_time = None
        self.elapsed_time = 0
        self.paused = True
        self.font = self.load_custom_font(54)
        self.text_color = (255, 255, 255)

    # ---------- FONT ---------- #
    # Load the custom game font.
    def load_custom_font(self, size):
        font_path = os.path.join(
            ROOT_PATH, "media", "graphics", "font", "Pixeboy.ttf"
        )
        return pygame.font.Font(font_path, size)

    # ---------- CONTROLS ---------- #
    # Start the timer.
    def start(self):
        self.paused = False
        self.start_time = time.time()

    # Pause the timer.
    def pause(self):
        if not self.paused:
            self.paused = True
            self.elapsed_time += time.time() - self.start_time

    # Resume the timer.
    def resume(self):
        if self.paused:
            self.paused = False
            self.start_time = time.time()

    # Reset the timer.
    def reset(self):
        self.start_time = None
        self.elapsed_time = 0
        self.paused = True

    # ---------- TIME CALCULATION ---------- #
    # Get the current time based on stopwatch or countdown mode.
    def get_time(self):
        if self.mode == "stopwatch":
            total = self.elapsed_time
            if not self.paused:
                total += time.time() - self.start_time
            return total
        else:
            total = self.countdown_time - self.elapsed_time
            if not self.paused:
                total -= time.time() - self.start_time
            return max(total, 0)

    # Update timer and stop the game when countdown reaches zero.
    def update(self):
        if self.mode == "countdown" and not self.paused:
            remaining = self.get_time()
            if remaining <= 0:
                self.pause()
                breakout.running = False

    # ---------- DRAW ---------- #
    # Draw the timer in the top-right corner.
    def draw(self):
        seconds = int(self.get_time())
        minutes = seconds // 60
        seconds = seconds % 60

        time_text = f"{minutes:02}:{seconds:02}"
        text_surface = self.font.render(time_text, True, self.text_color)

        text_rect = text_surface.get_rect(topright=(1165, 60))
        self.screen.blit(text_surface, text_rect)