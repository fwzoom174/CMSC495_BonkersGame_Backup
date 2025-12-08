import pygame
import os
import json
from common import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, ROOT_PATH

# --- Config path ---
config_path = "config.json"

def current_sfx_volume():
    """Read live sound volume (0–5) and convert to 0.0–1.0"""
    try:
        with open(config_path, "r") as f:
            cfg_local = json.load(f)
        level = cfg_local.get("sound_volume", 5)
        try:
            level = int(level)
        except:
            level = 5
        return max(0, min(5, level)) / 5.0
    except:
        return 1.0

# --- Pause Sounds ---
try:
    pause_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, "media", "audio", "pause.mp3"))
except:
    pause_sound = None

try:
    unpause_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, "media", "audio", "unpause.mp3"))
except:
    unpause_sound = None

def pause_overlay(snapshot):
    """Pause screen"""
    screen = pygame.display.get_surface()

    # Font setup
    font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
    font_big = pygame.font.Font(font_path, 120)
    font_small = pygame.font.Font(font_path, 48)

    clock = pygame.time.Clock()

    # Frozen frame
    screen.blit(snapshot, (0, 0))

    # Play pause sound with correct volume
    vol = current_sfx_volume()
    if pause_sound and vol > 0:
        pause_sound.set_volume(vol)
        pause_sound.play()

    while True:
        # Text
        title = font_big.render("PAUSED", True, YELLOW)
        quit_text = font_small.render("Press Q to Quit", True, WHITE)
        or_text = font_small.render("or", True, WHITE)
        resume_text = font_small.render("Press Space Bar to Resume", True, WHITE)

        # Center text block
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        screen.blit(or_text, (SCREEN_WIDTH // 2 - or_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))

        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Play unpause sound with correct volume
                    vol = current_sfx_volume()
                    if unpause_sound and vol > 0:
                        unpause_sound.set_volume(vol)
                        unpause_sound.play()
                    return "resume"
                if event.key == pygame.K_q:
                    return "menu"

        pygame.display.flip()
        clock.tick(60)
