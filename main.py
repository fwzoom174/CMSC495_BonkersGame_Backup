import sys
import pygame
import common

from common import RED, WHITE, GREEN, BLUE, SCREEN_WIDTH, SCREEN_HEIGHT
from scenes import breakout, how_to, highscores  # added highscores import for menu option


def main_menu():
    # Set up the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout Game - Menu")
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)

    # Added new "High Scores" button under How to Play
    title = font.render("Breakout Game", True, WHITE)
    play_button = small_font.render("Play", True, BLUE)
    quit_button = small_font.render("Quit", True, RED)
    how_button = small_font.render("How to Play", True, GREEN)
    high_button = small_font.render("High Scores", True, (255, 215, 0))  # gold color

    play_rect = play_button.get_rect(center=(SCREEN_WIDTH // 2, 320))
    how_rect = how_button.get_rect(center=(SCREEN_WIDTH // 2, 400))
    quit_rect = quit_button.get_rect(center=(SCREEN_WIDTH // 2, 560))
    high_rect = high_button.get_rect(center=(SCREEN_WIDTH // 2, 480))

    running = True
    while running:
        # Fill the screen with a gradient background
        common.draw_gradient_background(screen, (20, 20, 60), (0, 0, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Draw menu buttons (added high scores button in the middle)
        for button, rect in [
            (play_button, play_rect),
            (how_button, how_rect),
            (high_button, high_rect),
            (quit_button, quit_rect)
        ]:
            screen.blit(button, rect)

        # Detect mouse hover over buttons
        mouse_pos = pygame.mouse.get_pos()
        for rect in [play_rect, how_rect, quit_rect]:
            if rect.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                break
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Added new click option for High Scores and kept others the same
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    play_breakout(screen)
                elif how_rect.collidepoint(event.pos):
                    how_to.show_instructions(screen)
                elif high_rect.collidepoint(event.pos):
                    highscores.show_high_scores(screen)  # new function call
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                # LCTRL opens test menu for debug options
                if event.key == pygame.K_LCTRL:
                    open_test_menu(screen)
                elif event.key == pygame.K_SPACE:
                    play_breakout(screen)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        pygame.time.Clock().tick(60)


def open_test_menu(screen):
    """Simple text-based menu for choosing which test to run."""
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 36)
    running = True
    selection = None

    while running:
        screen.fill((0, 0, 0))
        title = font.render("TEST MODE", True, (255, 255, 255))
        option1 = small_font.render("1 - Regular Debug (1 Block)", True, (0, 200, 0))
        option2 = small_font.render("2 - Countdown Timer Test", True, (0, 200, 0))
        exit_text = small_font.render("ESC - Return to Menu", True, (200, 0, 0))

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 180))
        screen.blit(option1, (SCREEN_WIDTH // 2 - option1.get_width() // 2, 300))
        screen.blit(option2, (SCREEN_WIDTH // 2 - option2.get_width() // 2, 360))
        screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 450))

        # Added countdown timer test (debug option 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    play_breakout(screen, True)  # Regular debug mode
                    return
                elif event.key == pygame.K_2:
                    play_breakout(screen, "countdown")  # Countdown test mode
                    return
                elif event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)


def show_high_scores(screen):
    """Display the saved high score and best time (simple single-screen view)."""
    import os

    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 36)
    running = True

    # Loads score and time saved from last session
    records_path = os.path.join(os.path.dirname(__file__), "records.txt")
    high_score, best_time = 0, 0.0
    if os.path.exists(records_path):
        with open(records_path, "r") as f:
            lines = f.readlines()
            if len(lines) >= 1:
                high_score = int(lines[0].strip() or 0)
            if len(lines) >= 2:
                best_time = float(lines[1].strip() or 0.0)

    # Format time for cleaner display
    best_time_display = f"{int(best_time // 60):02}:{int(best_time % 60):02}"

    while running:
        screen.fill((0, 0, 0))
        title = font.render("HIGH SCORES", True, (255, 255, 255))
        score_text = small_font.render(f"High Score: {high_score}", True, (255, 215, 0))
        time_text = small_font.render(f"Best Time: {best_time_display}", True, (200, 200, 200))
        exit_text = small_font.render("Press ESC to return", True, (255, 100, 100))

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))
        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 350))
        screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 480))

        # ESC key closes the high score screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)


def play_breakout(screen, debug_mode=False):
    # Starts the breakout gameplay (normal, debug, or countdown)
    replay = True
    while replay:
        replay = breakout.play(screen, debug_mode)
    main_menu()


if __name__ == '__main__':
    # Initialize Pygame
    pygame.init()
    # Start the main menu and game
    main_menu()
