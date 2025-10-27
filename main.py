import sys
import pygame
import common

from common import RED, WHITE, GREEN, BLUE
from scenes import breakout, how_to

screen_width, screen_height = common.screen_width, common.screen_height

def main_menu():
    # Set up the screen
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Breakout Game - Menu")
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)

    # Set up the title and buttons
    title = font.render("Breakout Game", True, WHITE)
    play_button = small_font.render("Play", True, BLUE)
    quit_button = small_font.render("Quit", True, RED)
    how_button = small_font.render("How to Play", True, GREEN)

    play_rect = play_button.get_rect(center=(screen_width // 2, 320))
    how_rect = how_button.get_rect(center=(screen_width // 2, 400))
    quit_rect = quit_button.get_rect(center=(screen_width // 2, 480))

    running = True
    while running:
        # Fill the screen with a gradient background
        common.draw_gradient_background(screen, (20, 20, 60), (0, 0, 0))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 150))

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
                    breakout.play(screen)
                elif how_rect.collidepoint(event.pos):
                    how_to.show_instructions(screen)
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False

        # Update the display
        pygame.display.flip()
        pygame.time.Clock().tick(60)


if __name__ == '__main__':
    # Initialize Pygame
    pygame.init()
    # Start the main menu and game
    main_menu()