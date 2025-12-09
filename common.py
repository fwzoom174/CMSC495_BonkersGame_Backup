"""
This file defines global settings used across the game.
It stores screen size, colors, file paths, music loading,
and helper functions for saving config data and drawing
simple backgrounds.
"""

import pygame
import os
import json

# ---------- SCREEN SETTINGS ----------
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900

# ---------- COLOR SETUP ----------
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 128, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)

# Helpful list used to match bricks to colors
COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, CYAN]

# Base directory for all game files
ROOT_PATH = os.path.dirname(__file__)

# ---------- MUSIC LOADING ----------
pygame.mixer.init()

# Load music tracks used in menus, gameplay, and bosses
menu_music = pygame.mixer.Sound(os.path.join(ROOT_PATH, "media", "audio", "Music", "Space-main.wav"))
gameplay_music = pygame.mixer.Sound(os.path.join(ROOT_PATH, "media", "audio", "Music", "Game-main.wav"))
boss_music = pygame.mixer.Sound(os.path.join(ROOT_PATH, "media", "audio", "Music", "boss-fight-one.wav"))


def apply_music_volume(volume_level):
    """
    Set the music volume for all tracks.
    volume_level should be between 0 and 5.
    """
    vol = (max(0, min(volume_level, 5)) / 5) * 0.3
    menu_music.set_volume(vol)
    gameplay_music.set_volume(vol)
    boss_music.set_volume(vol)


def draw_gradient_background(screen, top_color, bottom_color):
    """
    Draw a simple vertical gradient from top_color to bottom_color.
    Used mainly in menu screens.
    """
    height = screen.get_height()
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (screen.get_width(), y))


def save_config(cfg):
    """Save game settings to config.json."""
    try:
        with open("config.json", "w") as f:
            json.dump(cfg, f, indent=4)
    except:
        print("Warning: Could not save config.json")