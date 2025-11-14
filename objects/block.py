import pygame
import os
from common import COLORS, ROOT_PATH

# Load brick images
brick_images_1 = {}
brick_images_2 = {}

# new sizes
BRICK1_SIZE = (60, 25)
BRICK2_SIZE = (35, 35)

color_names = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'cyan']
main_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'bricks')


def load_all_images():
    """Load every brick image one time only (not once per block)."""
    if brick_images_1:
        return

    for i, color_name in enumerate(color_names):

        # ---------- Brick 1 (normal) ----------
        file1 = f"{color_name}-brick.png"
        path1 = os.path.join(main_path, file1)

        if os.path.isfile(path1):
            img1 = pygame.image.load(path1).convert_alpha()
            brick_images_1[COLORS[i]] = img1
        else:
            brick_images_1[COLORS[i]] = None
            print(f"Warning: Missing {file1}")

        # ---------- Brick 2 (square) ----------
        file2 = f"{color_name}-brick-2.png"
        path2 = os.path.join(main_path, file2)

        if os.path.isfile(path2):
            img2 = pygame.image.load(path2).convert_alpha()
            brick_images_2[COLORS[i]] = img2
        else:
            brick_images_2[COLORS[i]] = None


def make_damaged(image):
    """Make a darker/damaged version without numpy."""
    if image is None:
        return None

    dull = image.copy()
    overlay = pygame.Surface(dull.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    dull.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return dull


class Block:
    def __init__(self, x, y, color, block_type=1):
        """
        block_type:
            1 = normal 1-HP brick
            2 = square 2-HP brick
        """
        load_all_images()

        # pick size
        if block_type == 2:
            self.width, self.height = BRICK2_SIZE
        else:
            self.width, self.height = BRICK1_SIZE

        # position is now given as TOP-LEFT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = color
        self.block_type = block_type

        # ------- Load correct base image -------
        if block_type == 2 and brick_images_2[color] is not None:
            base_image = brick_images_2[color]
            self.hp = 2
        else:
            base_image = brick_images_1[color]
            self.hp = 1

        self.max_hp = self.hp

        # scale image correctly to its own size
        if base_image is not None:
            self.image = pygame.transform.scale(base_image, (self.width, self.height))
        else:
            self.image = None

        # damaged version for 2HP bricks only
        if self.hp == 2 and self.image is not None:
            self.image_damaged = make_damaged(self.image)
        else:
            self.image_damaged = None

    # Called when hit
    def hit(self):
        """
        Returns True if block should be destroyed.
        Returns False if block stays (e.g., 2HP becomes 1HP).
        """
        if self.hp <= 1:
            return True

        # reduce HP
        self.hp -= 1

        # switch to damaged image
        if self.image_damaged:
            self.image = self.image_damaged

        return False
