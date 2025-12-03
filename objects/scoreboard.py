"""
This file creates the ScoreBoard for the game.
It loads the font, tracks score, lives, and high scores,
and draws the score display on the screen.
"""

import pygame
import os
from common import SCREEN_WIDTH, SCREEN_HEIGHT, ROOT_PATH


# ---------- IMAGE HELPERS ---------- #
# Remove transparent edges from a surface.
def crop_surface(surface):
    rect = surface.get_bounding_rect()
    return surface.subsurface(rect).copy()


# ---------- SCOREBOARD CLASS ---------- #
class ScoreBoard:
    # ---------- SETUP ---------- #
    # Create the scoreboard and load font, score values, and heart image.
    def __init__(self, screen):
        self.screen = screen

        font_path = os.path.join(
            ROOT_PATH, "media", "graphics", "font", "Pixeboy.ttf"
        )
        self.font = pygame.font.Font(font_path, 40)

        self.score = 0
        self.high_score = 0
        self.best_time = 0.0
        self.lives = 3

        self.load_high_score()

        # Cache text surfaces
        self._last_score = None
        self._last_high = None
        self._last_best_time = None
        self._score_surface = None
        self._high_surface = None
        self._best_time_surface = None

        heart_path = os.path.join(
            ROOT_PATH, "media", "graphics", "items", "heart.png"
        )
        raw_heart = pygame.image.load(heart_path).convert_alpha()
        raw_heart = crop_surface(raw_heart)
        self.heart_img = pygame.transform.scale(raw_heart, (25, 25))

    # ---------- CORE METHODS ---------- #
    # Add points to the score.
    def add_points(self, points: int):
        self.score += points

    # Subtract a life.
    def lose_life(self):
        self.lives -= 1

    # Reset score and lives for a new run.
    def reset(self):
        self.score = 0
        self.lives = 3

    # ---------- FILE HANDLING ---------- #
    # Load high score and best time from storage.
    def load_high_score(self):
        file_path = "records.txt"

        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("0\n0.0")

        with open(file_path, "r") as f:
            lines = f.readlines()

            if len(lines) >= 1:
                try:
                    self.high_score = int(lines[0].strip())
                except ValueError:
                    self.high_score = 0

            if len(lines) >= 2:
                try:
                    self.best_time = float(lines[1].strip())
                except ValueError:
                    self.best_time = 0.0

    # Save scores to text files for today and all-time history.
    def save_high_score(self, current_time=None, initials="YOU"):
        today_file = "today_scores.txt"
        alltime_file = "records_alltime.txt"
        records_file = "records.txt"

        initials = (initials or "").strip().upper()
        if initials == "":
            initials = "AAA"

        if current_time is None:
            current_time = 0.0

        line = f"{initials} {self.score} {current_time:.2f}\n"

        with open(today_file, "a", encoding="utf8") as f:
            f.write(line)

        with open(alltime_file, "a", encoding="utf8") as f:
            f.write(line)

        if self.score > self.high_score:
            self.high_score = self.score
            self.best_time = current_time
        elif self.score == self.high_score:
            if self.best_time == 0 or current_time < self.best_time:
                self.best_time = current_time

        with open(records_file, "w", encoding="utf8") as f:
            f.write(f"{self.high_score}\n{self.best_time}")

    # ---------- DRAW HUD ---------- #
    # Draw score, high score, best time, and hearts on the screen.
    def draw(self):
        margin = 65

        # Update cached score surface
        if self._last_score != self.score:
            self._score_surface = self.font.render(
                f"Score: {self.score}", True, (255, 255, 255)
            )
            self._last_score = self.score

        if self._last_high != self.high_score:
            self._high_surface = self.font.render(
                str(self.high_score), True, (255, 255, 255)
            )
            self._last_high = self.high_score

        if self._last_best_time != self.best_time:
            best_time_display = (
                f"{int(self.best_time // 60):02}:"
                f"{int(self.best_time % 60):02}"
            )
            self._best_time_surface = self.font.render(
                best_time_display, True, (255, 255, 255)
            )
            self._last_best_time = self.best_time

        # High score and best time (top left)
        left_x = 10
        top_y = 65

        label_high = self.font.render("HIGH:", True, (255, 255, 255))
        self.screen.blit(label_high, (left_x, top_y))

        self.screen.blit(
            self._high_surface,
            (left_x + label_high.get_width() + 10, top_y),
        )

        label_best = self.font.render("BEST TIME:", True, (255, 255, 255))
        best_start_x = (
            left_x
            + label_high.get_width()
            + self._high_surface.get_width()
            + 25
        )
        self.screen.blit(label_best, (best_start_x, top_y))

        if self._best_time_surface:
            self.screen.blit(
                self._best_time_surface,
                (best_start_x + label_best.get_width() + 10, top_y),
            )

        # Score (bottom left)
        score_y = (
            SCREEN_HEIGHT
            - margin
            - self._score_surface.get_height()
        )
        self.screen.blit(self._score_surface, (margin, score_y))

        # Lives and hearts (bottom right)
        lives_label = self.font.render("LIVES:", True, (255, 80, 80))

        fixed_right_margin = 220
        base_x = SCREEN_WIDTH - fixed_right_margin
        base_y = SCREEN_HEIGHT - 90

        self.screen.blit(lives_label, (base_x, base_y))

        heart_spacing = 8
        heart_w, heart_h = self.heart_img.get_size()

        hearts_start_x = base_x + lives_label.get_width() + 10
        hearts_y = base_y + (lives_label.get_height() - heart_h) // 2

        for i in range(self.lives):
            self.screen.blit(
                self.heart_img,
                (
                    hearts_start_x + i * (heart_w + heart_spacing),
                    hearts_y,
                ),
            )