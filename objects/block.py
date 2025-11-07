import pygame
import os
from common import COLORS, ROOT_PATH

# Load brick images
brick_images = {}
color_names = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'cyan']
main_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'bricks')

def load_images(rect):
    for i, color_name in enumerate(color_names):
        file = f"{color_name}-brick.png"
        if os.path.isfile(os.path.join(main_path, file)):
            img = pygame.image.load(os.path.join(main_path, file))
            brick_images[COLORS[i]] = pygame.transform.scale(img, (rect.width, rect.height))
        else:
            brick_images[COLORS[i]] = None
            print(f"Warning: Could not load {os.path.join(main_path, file)}")


class Block:
    def __init__(self, rect, color):
        self.rect = rect
        self.color = color
        load_images(rect)
        self.image = brick_images[color]
