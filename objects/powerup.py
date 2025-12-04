"""
This file creates the PowerUp and BlueBlast objects for the game.
It loads their images, moves them on the screen,
and checks when they should be removed.
"""

import pygame
import os
from common import ROOT_PATH, SCREEN_HEIGHT

# ---------- POWERUP CLASS ---------- #
# Power up object that falls toward the player.
class PowerUp:
    # ---------- SETUP ---------- #
    def __init__(self, x, y, powerup_type="blast"):
        self.x = x
        self.y = y
        self.velocity_y = 4
        self.type = powerup_type  # "blast", "small_paddle", "triple_ball"

        # Triple ball size update
        if powerup_type == "triple_ball":
            self.width = 60
            self.height = 60
        else:
            self.width = 30
            self.height = 30

        # Load power up image
        self.image = None
        try:
            if powerup_type == "blast":
                img = pygame.image.load(
                    os.path.join(
                        ROOT_PATH, "media", "graphics", "Particles", "blast.png"
                    )
                )
            elif powerup_type == "small_paddle":
                img = pygame.image.load(
                    os.path.join(
                        ROOT_PATH, "media", "graphics", "Particles", "small paddle.png"
                    )
                )
            elif powerup_type == "triple_ball":
                img = pygame.image.load(
                    os.path.join(
                        ROOT_PATH, "media", "graphics", "Particles", "Tripleball.png"
                    )
                )
            elif powerup_type == "big_paddle":
                img = pygame.image.load(
                    os.path.join(
                        ROOT_PATH, "media", "graphics", "Particles", "big paddle.png"
                    )
                )
            elif powerup_type == "slow":
                img = pygame.image.load(
                    os.path.join(
                        ROOT_PATH, "media", "graphics", "Particles", "slow.png"
                    )
                )

            elif powerup_type == "shield":
                img = pygame.image.load(
                    os.path.join(
                        ROOT_PATH, "media", "graphics", "Particles", "shield.png"
                    )
                )

            elif powerup_type == "reverse":
                img = pygame.image.load(
                    os.path.join(
                        ROOT_PATH, "media", "graphics", "Particles", "reverse.png"
                    )
                )
            self.image = pygame.transform.scale(img, (self.width, self.height))

        except Exception as e:
            print(f"Warning: Could not load {powerup_type} image - {e}")
            self.debug_color = {
                "blast": (0, 150, 255),
                "small_paddle": (255, 165, 0),
                "triple_ball": (0, 255, 0),
                "big_paddle": (255, 0, 200),
            }.get(powerup_type, (0, 100, 255))

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    # ---------- MOVEMENT ---------- #
    # Move the power up downward.
    def update(self):
        self.y += self.velocity_y * slow_multiplier
        self.rect.x = self.x
        self.rect.y = self.y

    # ---------- DRAW ---------- #
    # Draw the power up on the screen.
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(
                screen,
                getattr(self, "debug_color", (0, 100, 255)),
                (self.x, self.y, self.width, self.height),
            )

    # ---------- CHECK REMOVAL ---------- #
    # Check if the power up has moved below the screen.
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT


# ---------- BLUEBLAST CLASS ---------- #
# Blue blast projectile that moves upward.
class BlueBlast:
    # ---------- SETUP ---------- #
    def __init__(self, x, y):
        self.width = 20
        self.height = 40
        self.x = x
        self.y = y
        self.velocity_y = -8

        self.image = None
        try:
            img = pygame.image.load(
                os.path.join(
                    ROOT_PATH,
                    "media",
                    "graphics",
                    "Particles",
                    "blue-blast.png",
                )
            )
            self.image = pygame.transform.scale(
                img, (self.width, self.height)
            )
        except Exception as e:
            print(f"Warning: Could not load blue-blast.png - {e}")

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    # ---------- MOVEMENT ---------- #
    # Move the blast upward.
    def update(self):
        self.y += self.velocity_y
        self.rect.x = self.x
        self.rect.y = self.y

    # ---------- DRAW ---------- #
    # Draw the blast on the screen.
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(
                screen, (0, 150, 255),
                (self.x, self.y, self.width, self.height)
            )

    # ---------- CHECK REMOVAL ---------- #
    # Check if the blast has moved above the limit line.
    def is_off_screen(self):
        return self.y < 120