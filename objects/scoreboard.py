import pygame
import os
from common import SCREEN_WIDTH, SCREEN_HEIGHT, ROOT_PATH


def crop_surface(surface):
    """Remove transparent edges from an image."""
    rect = surface.get_bounding_rect()
    return surface.subsurface(rect).copy()

class ScoreBoard:
    """Displays and manages the score, lives, and high score."""

    def __init__(self, screen):
        self.screen = screen

        # Load font
        font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
        self.font = pygame.font.Font(font_path, 40)

        # Score values
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

        heart_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'items', 'heart.png')
        raw_heart = pygame.image.load(heart_path).convert_alpha()

        # Auto-crop transparent edges
        raw_heart = crop_surface(raw_heart)

        # Scale after cropping (clean edges)
        self.heart_img = pygame.transform.scale(raw_heart, (25, 25))

    # ---------- CORE METHODS ---------- #
    def add_points(self, points: int):
        self.score += points

    def lose_life(self):
        self.lives -= 1

    def reset(self):
        self.score = 0
        self.lives = 3

    # ---------- FILE HANDLING ---------- #
    def load_high_score(self):
        file_path = "records.txt"

        # Create file if missing
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("0\n0.0")

        # Load values
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

    def save_high_score(self, current_time=None, initials="YOU"):
        """Save new high score and record both today's and all-time scores."""
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

        # Update quick display file used in game HUD
        if self.score > self.high_score:
            self.high_score = self.score
            self.best_time = current_time
        elif self.score == self.high_score:
            if self.best_time == 0 or current_time < self.best_time:
                self.best_time = current_time

        with open(records_file, "w", encoding="utf8") as f:
            f.write(f"{self.high_score}\n{self.best_time}")


    # ---------- DRAW METHOD ---------- #
    def draw(self):
        margin = 65

        # Update cached text
        if self._last_score != self.score:
            self._score_surface = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self._last_score = self.score

        if self._last_high != self.high_score:
            self._high_surface = self.font.render(str(self.high_score), True, (255, 255, 255))
            self._last_high = self.high_score

        if self._last_best_time != self.best_time:
            best_time_display = f"{int(self.best_time // 60):02}:{int(self.best_time % 60):02}"
            self._best_time_surface = self.font.render(best_time_display, True, (255, 255, 255))
            self._last_best_time = self.best_time

        # ---------- TOP LEFT: HIGH + BEST TIME ----------
        left_x = 10
        top_y = 65

        # HIGH
        label_high = self.font.render("HIGH:", True, (255, 255, 255))
        self.screen.blit(label_high, (left_x, top_y))

        self.screen.blit(
            self._high_surface,
            (left_x + label_high.get_width() + 10, top_y)
        )

        # BEST TIME
        label_best = self.font.render("BEST TIME:", True, (255, 255, 255))
        best_start_x = left_x + label_high.get_width() + self._high_surface.get_width() + 25
        self.screen.blit(label_best, (best_start_x, top_y))

        if self._best_time_surface:
            self.screen.blit(
                self._best_time_surface,
                (best_start_x + label_best.get_width() + 10, top_y)
            )

        # ---------- BOTTOM LEFT: SCORE ----------
        score_y = SCREEN_HEIGHT - margin - self._score_surface.get_height()
        self.screen.blit(self._score_surface, (margin, score_y))

        # ---------- BOTTOM RIGHT: LIVES + HEARTS ----------
        lives_label = self.font.render("LIVES:", True, (255, 80, 80))

        fixed_right_margin = 220
        base_x = SCREEN_WIDTH - fixed_right_margin
        base_y = SCREEN_HEIGHT - 90

        # Draw the LIVES: text
        self.screen.blit(lives_label, (base_x, base_y))

        # Hearts appear to the RIGHT of the text
        heart_spacing = 8
        heart_w, heart_h = self.heart_img.get_size()

        hearts_start_x = base_x + lives_label.get_width() + 10
        hearts_y = base_y + (lives_label.get_height() - heart_h) // 2

        for i in range(self.lives):
            self.screen.blit(self.heart_img, (hearts_start_x + i * (heart_w + heart_spacing), hearts_y))
