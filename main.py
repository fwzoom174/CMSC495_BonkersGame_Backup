import sys
import pygame
import common

from common import RED, WHITE, GREEN, BLUE, SCREEN_WIDTH, SCREEN_HEIGHT
from scenes import breakout, how_to

def main_menu():
    # Set up the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout Game - Menu")
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)

    # Set up the title and buttons
    title = font.render("Breakout Game", True, WHITE)
    play_button = small_font.render("Play", True, BLUE)
    quit_button = small_font.render("Quit", True, RED)
    how_button = small_font.render("How to Play", True, GREEN)

    play_rect = play_button.get_rect(center=(SCREEN_WIDTH // 2, 320))
    how_rect = how_button.get_rect(center=(SCREEN_WIDTH // 2, 400))
    quit_rect = quit_button.get_rect(center=(SCREEN_WIDTH // 2, 480))

    running = True
    while running:
        # Fill the screen with a gradient background
        common.draw_gradient_background(screen, (20, 20, 60), (0, 0, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Draw menu buttons
        for button, rect in [(play_button, play_rect), (how_button, how_rect), (quit_button, quit_rect)]:
            screen.blit(button, rect)

        # Detect mouse hover over buttons
        mouse_pos = pygame.mouse.get_pos()
        for rect in [play_rect, how_rect, quit_rect]:
            if rect.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                break
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    play_breakout(screen)
                elif how_rect.collidepoint(event.pos):
                    how_to.show_instructions(screen)
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL:
                    play_breakout(screen, True)
                if event.key == pygame.K_SPACE:
                    play_breakout(screen)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Update the display
        pygame.display.flip()
        pygame.time.Clock().tick(60)


def play_breakout(screen, debug_mode=False):
    replay = True
    while replay:
        replay = breakout.play(screen, debug_mode)
    main_menu()

if __name__ == '__main__':
    # Initialize Pygame
    pygame.init()
    # Start the main menu and game
    main_menu()
