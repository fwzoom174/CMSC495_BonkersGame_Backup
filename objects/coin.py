"""
This file creates the Coin object for the game.
It loads the coin image, moves the coin downward,
and checks when the coin goes off the screen.
"""

import os
import pygame
from common import ROOT_PATH, SCREEN_HEIGHT


# ---------- COIN CLASS ---------- #
# Represents one falling coin used for item drops.
class Coin:
    # Set up the coin position, size, and image.
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.width = 20
        self.height = 20
        self.velocity_y = 4

        # Rectangle used for collision checks
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Load and scale the coin image
        try:
            img_path = os.path.join(
                ROOT_PATH,
                "media",
                "graphics",
                "Particles",
                "coin.png"
            )
            self.image = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(
                self.image,
                (self.width, self.height)
            )
        except Exception:
            self.image = None
            print("Warning: Could not load coin.png")

    # Move the coin downward each frame.
    def update(self):
        self.y += self.velocity_y
        self.rect.y = self.y

    # Draw the coin on the screen.
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.circle(
                screen,
                (255, 215, 0),
                (int(self.x + self.width // 2),
                 int(self.y + self.height // 2)),
                self.width // 2
            )

    # Check if the coin has moved below the screen.
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT