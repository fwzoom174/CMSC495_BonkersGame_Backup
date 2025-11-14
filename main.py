import sys
import pygame
import common

from common import RED, WHITE, GREEN, BLUE, SCREEN_WIDTH, SCREEN_HEIGHT
from scenes import breakout, how_to, highscores

# ---------- SOUND & GRAPHICS LOADING ----------
# Initialize the mixer for sound
pygame.mixer.init()

# Load sound effects
try:
    menu_click_sound = pygame.mixer.Sound("media/audio/media_audio_selection_click.wav")
except:
    print("Warning: Could not load menu click sound.")
    menu_click_sound = None

# Load background image
try:
    menu_background = pygame.image.load("media/graphics/background/back-landscape-grid.png")
except:
    print("Warning: Could not load background image.")
    menu_background = None

# ---------- MAIN MENU ----------
def main_menu():
    # Set up the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout Game - Menu")
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)

    # Main menu text
    title = font.render("Breakout Game", True, WHITE)
    play_button = small_font.render("Play", True, BLUE)
    quit_button = small_font.render("Quit", True, RED)
    how_button = small_font.render("How to Play", True, GREEN)
    high_button = small_font.render("High Scores", True, (255, 215, 0))

    play_rect = play_button.get_rect(center=(SCREEN_WIDTH // 2, 320))
    how_rect = how_button.get_rect(center=(SCREEN_WIDTH // 2, 400))
    quit_rect = quit_button.get_rect(center=(SCREEN_WIDTH // 2, 560))
    high_rect = high_button.get_rect(center=(SCREEN_WIDTH // 2, 480))

    running = True
    while running:
        # Draw background
        if menu_background:
            scaled_bg = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
        else:
            common.draw_gradient_background(screen, (20, 20, 60), (0, 0, 0))

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Draw menu buttons
        for button, rect in [
            (play_button, play_rect),
            (how_button, how_rect),
            (high_button, high_rect),
            (quit_button, quit_rect)
        ]:
            screen.blit(button, rect)

        # Mouse hover check
        mouse_pos = pygame.mouse.get_pos()
        for rect in [play_rect, how_rect, high_rect, quit_rect]:
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
                    if menu_click_sound:
                        menu_click_sound.play()
                    play_breakout(screen)
                elif how_rect.collidepoint(event.pos):
                    if menu_click_sound:
                        menu_click_sound.play()
                    how_to.show_instructions(screen)
                elif high_rect.collidepoint(event.pos):
                    if menu_click_sound:
                        menu_click_sound.play()
                    highscores.show_high_scores(screen)
                elif quit_rect.collidepoint(event.pos):
                    if menu_click_sound:
                        menu_click_sound.play()
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                # LCTRL opens test menu for debug options
                if event.key == pygame.K_LCTRL:
                    open_test_menu(screen)
                elif event.key == pygame.K_SPACE:
                    if menu_click_sound:
                        menu_click_sound.play()
                    play_breakout(screen)
                elif event.key == pygame.K_ESCAPE:
                    if menu_click_sound:
                        menu_click_sound.play()
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# ---------- TEST/DEBUG MENU ----------
def open_test_menu(screen):
    """Simple text-based menu for choosing which test/debug to run."""
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 36)
    running = True

    while running:
        screen.fill((0, 0, 0))

        title = font.render("TEST MODE", True, (255, 255, 255))
        option1 = small_font.render("1 - Regular Debug (1 Block)", True, (0, 200, 0))
        option2 = small_font.render("2 - Countdown Timer Test", True, (0, 200, 0))
        option3 = small_font.render("3 - Start at Level 1", True, (200, 200, 0))
        option4 = small_font.render("4 - Start at Level 2", True, (200, 200, 0))
        option5 = small_font.render("5 - Start at Level 3", True, (200, 200, 0))
        option6 = small_font.render("6 - Start at Level 4", True, (200, 200, 0))
        option7 = small_font.render("7 - Start at Level 5", True, (200, 200, 0))
        exit_text = small_font.render("ESC - Return to Menu", True, (200, 0, 0))

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        screen.blit(option1, (SCREEN_WIDTH // 2 - option1.get_width() // 2, 260))
        screen.blit(option2, (SCREEN_WIDTH // 2 - option2.get_width() // 2, 310))
        screen.blit(option3, (SCREEN_WIDTH // 2 - option3.get_width() // 2, 360))
        screen.blit(option4, (SCREEN_WIDTH // 2 - option4.get_width() // 2, 410))
        screen.blit(option5, (SCREEN_WIDTH // 2 - option5.get_width() // 2, 460))
        screen.blit(option6, (SCREEN_WIDTH // 2 - option6.get_width() // 2, 510))
        screen.blit(option7, (SCREEN_WIDTH // 2 - option7.get_width() // 2, 560))
        screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 620))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    play_breakout(screen, "one_block")
                    return
                elif event.key == pygame.K_2:
                    play_breakout(screen, "countdown")
                    return
                elif event.key == pygame.K_3:
                    play_breakout(screen, "level_1")
                    return
                elif event.key == pygame.K_4:
                    play_breakout(screen, "level_2")
                    return
                elif event.key == pygame.K_5:
                    play_breakout(screen, "level_3")
                    return
                elif event.key == pygame.K_6:
                    play_breakout(screen, "level_4")
                    return
                elif event.key == pygame.K_7:
                    play_breakout(screen, "level_5")
                    return
                elif event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# ---------- GAME LAUNCHER ----------
def play_breakout(screen, debug_mode=False):
    # Starts the breakout gameplay (normal, debug, or countdown)
    replay = True
    while replay:
        replay = breakout.play(screen, debug_mode)
    main_menu()

# ---------- MAIN ENTRY POINT ----------
if __name__ == '__main__':
    # Initialize Pygame
    pygame.init()
    # Start the main menu and game
    main_menu()
