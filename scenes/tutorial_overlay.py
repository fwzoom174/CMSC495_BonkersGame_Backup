import pygame
import os
import sys
from common import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, YELLOW, ROOT_PATH


# ---------- TUTORIAL OVERLAY ----------
def show_tutorial_overlay(snapshot):
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
    font_big = pygame.font.Font(font_path, 72)
    font_small = pygame.font.Font(font_path, 36)

    # Load key images
    tutorial_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'tutorial')
    arrow_img = pygame.image.load(os.path.join(tutorial_path, 'arrow_keys.png'))
    wasd_img = pygame.image.load(os.path.join(tutorial_path, 'wasd_keys.png'))

    arrow_img = pygame.transform.scale(arrow_img, (150, 150))
    wasd_img = pygame.transform.scale(wasd_img, (150, 150))

    while True:
        screen.blit(snapshot, (0, 0))

        title = font_big.render("HOW TO PLAY", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))

        # Arrow keys + text
        screen.blit(arrow_img, (SCREEN_WIDTH // 2 - 220, 180))
        arrow_text = font_small.render("Use ARROW KEYS to move", True, WHITE)
        screen.blit(arrow_text, (SCREEN_WIDTH // 2 - arrow_text.get_width() // 2, 340))

        # WASD keys + text
        screen.blit(wasd_img, (SCREEN_WIDTH // 2 + 70, 180))
        wasd_text = font_small.render("or use A and D keys", True, WHITE)
        screen.blit(wasd_text, (SCREEN_WIDTH // 2 - wasd_text.get_width() // 2, 340))

        # Instructions
        space_text = font_small.render("SPACE to launch the ball", True, WHITE)
        esc_text = font_small.render("ESC to pause the game", True, WHITE)
        start_text = font_small.render("PRESS ENTER OR SPACE TO BEGIN", True, RED)

        screen.blit(space_text, (SCREEN_WIDTH // 2 - space_text.get_width() // 2, 400))
        screen.blit(esc_text, (SCREEN_WIDTH // 2 - esc_text.get_width() // 2, 440))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 510))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    return

        pygame.display.flip()
        clock.tick(60)
