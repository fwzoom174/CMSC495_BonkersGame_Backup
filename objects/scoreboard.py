# Early draft of the scoreboard system

import pygame
import os
from common import SCREEN_WIDTH, SCREEN_HEIGHT

# Constants for block spacing (used for visual alignment)
BLOCK_WIDTH = 60
BLOCK_SPACE = 10

class ScoreBoard:
    """Displays and manages the score, lives, and high score."""

    def __init__(self, screen):
        self.screen = screen
        font_path = os.path.join(os.path.dirname(__file__), '..', 'media', 'graphics', 'font', 'Pixeboy.ttf')
        self.font = pygame.font.Font(font_path, 50)  # Pixel font
        self.score = 0
        self.high_score = 0
        self.best_time = 0.0
        self.lives = 3
        self.load_high_score()

        # Cache last rendered text to reduce flicker
        self._last_score = None
        self._last_high = None
        self._last_lives = None
        self._last_best_time = None
        self._score_surface = None
        self._high_surface = None
        self._lives_surface = None
        self._best_time_surface = None

    # ---------- CORE METHODS ---------- #
    def add_points(self, points: int):
        """Add points to the player's score when a block is hit."""
        self.score += points

    def lose_life(self):
        """Decrease lives by one when the ball falls below the paddle."""
        self.lives -= 1

    def reset(self):
        """Reset score and lives for a new game."""
        self.score = 0
        self.lives = 3

    # ---------- FILE HANDLING ---------- #
    def load_high_score(self):
        """Load or create records.txt to store the highest score and best time."""
        file_path = os.path.join(os.path.dirname(__file__), "../records.txt")
        file_path = os.path.abspath(file_path)

        # Create file if it does not exist
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("0\n0.0")

        # Updated this to load both high score and best time values
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
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        today_file = os.path.join(base_path, "today_scores.txt")
        alltime_file = os.path.join(base_path, "records_alltime.txt")

        # Added: save player initials, score, and time to daily records
        with open(today_file, "a") as f:
            f.write(f"{initials} {self.score} {current_time or 0}\n")

        # Handle all-time records with sorting by score and time
        alltime_records = []
        if os.path.exists(alltime_file):
            with open(alltime_file, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        name, score, time_val = parts
                        alltime_records.append((name.upper(), int(score), float(time_val)))

        # Add the new record to the list
        alltime_records.append((initials, self.score, current_time or 0.0))

        # Sort by highest score, then fastest completion time
        alltime_records.sort(key=lambda x: (-x[1], x[2]))

        # Keep top 10 records in file
        alltime_records = alltime_records[:10]

        # Write the updated leaderboard back to file
        with open(alltime_file, "w") as f:
            for entry in alltime_records:
                name, score, time_val = entry
                f.write(f"{name} {score} {time_val}\n")

        # Standard single-record save for quick display on screen
        file_path = os.path.join(base_path, "records.txt")
        if self.score > self.high_score:
            self.high_score = self.score
            if current_time is not None:
                self.best_time = current_time
        elif self.score == self.high_score and current_time is not None:
            if self.best_time == 0 or current_time < self.best_time:
                self.best_time = current_time

        with open(file_path, "w") as f:
            f.write(f"{self.high_score}\n{self.best_time}")

    # ---------- DRAW METHOD ---------- #
    def draw(self):
        """Draw scoreboard elements on screen:
        - High score and best time at top-left
        - Score at bottom-left
        - Lives at bottom-right
        """

        margin = 65  # distance from screen edges

        # Added check for best time display (beside high score)
        if self._last_score != self.score:
            self._score_surface = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self._last_score = self.score
        if self._last_high != self.high_score:
            self._high_surface = self.font.render(f"High: {self.high_score}", True, (255, 255, 255))
            self._last_high = self.high_score
        if self._last_best_time != self.best_time:
            best_time_display = f"{int(self.best_time // 60):02}:{int(self.best_time % 60):02}"
            self._best_time_surface = self.font.render(f"Best Time: {best_time_display}", True, (255, 255, 255))
            self._last_best_time = self.best_time
        if self._last_lives != self.lives:
            self._lives_surface = self.font.render(f"Lives: {self.lives}", True, (255, 80, 80))
            self._last_lives = self.lives

        # Updated layout: high score and best time shown side-by-side at top-left
        high_x, high_y = 10, 60
        self.screen.blit(self._high_surface, (high_x, high_y))

        # Added positioning to place best time next to high score
        if self._best_time_surface:
            best_x = high_x + self._high_surface.get_width() + 30
            best_y = high_y + 2
            self.screen.blit(self._best_time_surface, (best_x, best_y))

        # Score shown bottom-left
        score_y = SCREEN_HEIGHT - margin - self._score_surface.get_height()
        self.screen.blit(self._score_surface, (margin, score_y))

        # Lives shown bottom-right
        lives_x = SCREEN_WIDTH - margin - self._lives_surface.get_width()
        lives_y = SCREEN_HEIGHT - margin - self._lives_surface.get_height()
        self.screen.blit(self._lives_surface, (lives_x, lives_y))
