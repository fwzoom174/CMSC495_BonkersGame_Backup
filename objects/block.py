"""
This file creates the Brick object for the game.
It loads the brick images, sets the brick size and color,
and updates how the brick looks when it takes damage.
"""

import os
import pygame
from common import COLORS, ROOT_PATH

# Image caches for each brick type.
# Images load once and are reused for speed.
brick_images_1 = {}
brick_images_2 = {}

# Brick sizes
BRICK1_SIZE = (60, 25)   # Normal rectangle brick
BRICK2_SIZE = (35, 35)   # Square stronger brick

color_names = ["red", "orange", "yellow", "green", "blue", "purple", "cyan"]
main_path = os.path.join(ROOT_PATH, "media", "graphics", "bricks")


# ---------- IMAGE LOADING ---------- #
# Load all brick images one time so each block does not reload them.
def load_all_images():
    if brick_images_1:
        return  # Already loaded

    global crack_overlay_img
    crack_path = os.path.join(main_path, "crack_overlay.png")

    # Load cracked overlay for damaged 2-hit bricks
    if os.path.isfile(crack_path):
        crack_overlay_img = pygame.image.load(crack_path).convert_alpha()
        crack_overlay_img = pygame.transform.scale(
            crack_overlay_img, BRICK2_SIZE
        )
    else:
        crack_overlay_img = None

    # Load normal and square bricks for all colors
    for i, color_name in enumerate(color_names):

        # Normal brick image
        file1 = f"{color_name}-brick.png"
        path1 = os.path.join(main_path, file1)

        if os.path.isfile(path1):
            img1 = pygame.image.load(path1).convert_alpha()
            brick_images_1[COLORS[i]] = img1
        else:
            brick_images_1[COLORS[i]] = None
            print(f"Warning: Missing {file1}")

        # Square brick image (used for stronger bricks)
        file2 = f"{color_name}-brick-2.png"
        path2 = os.path.join(main_path, file2)

        if os.path.isfile(path2):
            img2 = pygame.image.load(path2).convert_alpha()
            brick_images_2[COLORS[i]] = img2
        else:
            brick_images_2[COLORS[i]] = None


# ---------- BLOCK CLASS ---------- #
# Represents a single brick in the game.
class Block:
    # Set up brick size, image, color, and hit points.
    def __init__(self, x, y, color, block_type=1):
        load_all_images()

        # Pick size based on brick strength
        if block_type == 2:
            self.width, self.height = BRICK2_SIZE  # Stronger square brick
        else:
            self.width, self.height = BRICK1_SIZE  # Normal rectangle brick

        # Rectangle position
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = color
        self.block_type = block_type

        # Select base image and hit points
        if block_type == 2 and brick_images_2[color] is not None:
            base_image = brick_images_2[color]
            self.hp = 2  # Strong brick takes 2 hits
        else:
            base_image = brick_images_1[color]
            self.hp = 1

        self.max_hp = self.hp  # Store original HP

        # Scale brick image to match size
        if base_image is not None:
            self.image = pygame.transform.scale(
                base_image, (self.width, self.height)
            )
        else:
            self.image = None

        # Create cracked version for 2-hit bricks
        if self.hp == 2 and self.image is not None and crack_overlay_img:
            damaged = self.image.copy()
            damaged.blit(crack_overlay_img, (0, 0))
            self.image_damaged = damaged
        else:
            self.image_damaged = None

    # Handle brick damage and swap to cracked image.
    def hit(self):
        if self.hp <= 1:
            return True  # Brick breaks

        self.hp -= 1  # Lose one hit point

        # Switch to cracked image if available
        if self.image_damaged:
            self.image = self.image_damaged

        return False