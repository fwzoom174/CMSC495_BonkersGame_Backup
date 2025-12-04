"""
This file controls the pause screen.
It shows the paused message, waits for player input,
and plays the pause and unpause sounds.
"""

import pygame
import os
import json
from common import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, ROOT_PATH

# ---------- CONFIG ----------

# Path to the game settings file
config_path = "config.json"


def current_sfx_volume():
    """Read sound volume (0–5) from config.json and return it as 0.0–1.0."""
    try:
        with open(config_path, "r") as f:
            cfg_local = json.load(f)

        level = cfg_local.get("sound_volume", 5)

        # Make sure the value is a number
        try:
            level = int(level)
        except:
            level = 5

        # Keep volume in range and convert to percent
        return max(0, min(5, level)) / 5.0

    except:
        return 1.0  # Default full volume if something goes wrong


# ---------- SOUND LOADING ----------

# Pause sound effect
try:
    pause_sound = pygame.mixer.Sound(
        os.path.join(ROOT_PATH, "media", "audio", "pause.mp3")
    )
except:
    pause_sound = None

# Unpause sound effect
try:
    unpause_sound = pygame.mixer.Sound(
        os.path.join(ROOT_PATH, "media", "audio", "unpause.mp3")
    )
except:
    unpause_sound = None


# ---------- PAUSE OVERLAY ----------

def pause_overlay(snapshot):
    """Show the pause screen and wait for resume or quit."""

    # Get the game's current display surface
    screen = pygame.display.get_surface()

    # Load fonts
    font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
    font_big = pygame.font.Font(font_path, 120)
    font_small = pygame.font.Font(font_path, 48)

    clock = pygame.time.Clock()

    # Display the frozen background image
    screen.blit(snapshot, (0, 0))

    # Play pause sound once
    vol = current_sfx_volume()
    if pause_sound and vol > 0:
        pause_sound.set_volume(vol)
        pause_sound.play()

    # Pause loop
    while True:

        # Create the text to display
        title = font_big.render("PAUSED", True, YELLOW)
        quit_text = font_small.render("Press Q to Quit", True, (0, 255, 255))
        or_text = font_small.render("or", True, (0, 255, 255))
        resume_text = font_small.render("Press Space Bar to Resume", True, (0, 255, 255))

        # Draw centered text
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(or_text, (SCREEN_WIDTH // 2 - or_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))

        # Handle input
        for event in pygame.event.get():

            # Window close button
            if event.type == pygame.QUIT:
                return "menu"

            # Key presses
            if event.type == pygame.KEYDOWN:

                # Resume game
                if event.key == pygame.K_SPACE:
                    vol = current_sfx_volume()
                    if unpause_sound and vol > 0:
                        unpause_sound.set_volume(vol)
                        unpause_sound.play()
                    return "resume"

                # Quit to menu
                if event.key == pygame.K_q:
                    return "menu"

        pygame.display.flip()
        clock.tick(60)