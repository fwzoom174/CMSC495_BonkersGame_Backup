import pygame
import os
from common import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW

def pause_overlay(snapshot):
    """Pause screen"""
    screen = pygame.display.get_surface()

    # Font setup
    font_path = os.path.join(os.path.dirname(__file__), '..', 'media', 'graphics', 'font', 'Pixeboy.ttf')
    font_big = pygame.font.Font(font_path, 120)
    font_small = pygame.font.Font(font_path, 48)

    clock = pygame.time.Clock()

    # Frozen frame
    screen.blit(snapshot, (0, 0))

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
                    return "resume"
                if event.key == pygame.K_q:
                    return "menu"

        pygame.display.flip()
        clock.tick(60)
