# scoreboard.py
# Early draft of the scoreboard system
# Handles player score, lives, and high score tracking

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
        self.font = pygame.font.SysFont("Verdana", 26)  # clean, readable font
        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.load_high_score()

        # Cache last rendered text to reduce flicker and improve performance
        self._last_score = None
        self._last_high = None
        self._last_lives = None
        self._score_surface = None
        self._high_surface = None
        self._lives_surface = None

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
        """Load or create records.txt to store the highest score."""
        file_path = os.path.join(os.path.dirname(__file__), "../records.txt")
        file_path = os.path.abspath(file_path)

        # Create the file if it does not exist
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("0")

        # Read and store the current high score
        with open(file_path, "r") as f:
            data = f.read().strip()
            self.high_score = int(data) if data.isdigit() else 0

    def save_high_score(self):
        """Save a new high score if the player beats the old one."""
        file_path = os.path.join(os.path.dirname(__file__), "../records.txt")
        file_path = os.path.abspath(file_path)

        if self.score > self.high_score:
            with open(file_path, "w") as f:
                f.write(str(self.score))
            self.high_score = self.score

    # ---------- DRAW METHOD ---------- #
    def draw(self):
        """Draw scoreboard elements on screen:
        - High score at top-left
        - Score at bottom-left
        - Lives at bottom-right
        """

        margin = 25  # distance from screen edges

        # Update cached surfaces only when values change
        if self._last_score != self.score:
            self._score_surface = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self._last_score = self.score
        if self._last_high != self.high_score:
            self._high_surface = self.font.render(f"High: {self.high_score}", True, (255, 255, 0))
            self._last_high = self.high_score
        if self._last_lives != self.lives:
            self._lives_surface = self.font.render(f"Lives: {self.lives}", True, (255, 80, 80))
            self._last_lives = self.lives

        # Draw high score near top-left corner
        self.screen.blit(self._high_surface, (10, 5))

        # Draw score at bottom-left
        score_y = SCREEN_HEIGHT - margin - self._score_surface.get_height()
        self.screen.blit(self._score_surface, (margin, score_y))

        # Draw lives at bottom-right
        lives_x = SCREEN_WIDTH - margin - self._lives_surface.get_width()
        lives_y = SCREEN_HEIGHT - margin - self._lives_surface.get_height()
        self.screen.blit(self._lives_surface, (lives_x, lives_y))
