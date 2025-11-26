import sys
import pygame
import common
import os
import json

from common import RED, WHITE, GREEN, BLUE, SCREEN_WIDTH, SCREEN_HEIGHT, ROOT_PATH
from scenes import breakout, highscores

pygame.mixer.init()

try:
    menu_click_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, "media", "audio", "media_audio_selection_click.wav"))
except:
    print("Warning: Could not load menu click sound.")
    menu_click_sound = None

try:
    menu_background = pygame.image.load(os.path.join(ROOT_PATH, "media", "graphics", "background", "back-landscape-grid.png"))
except:
    print("Warning: Could not load background image.")
    menu_background = None

# ---- Load or create config ----
config_path = "config.json"

if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)

    # ensure key exists
    config.setdefault("tutorial_enabled", True)

else:
    config = {
        "tutorial_enabled": True
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


# ---------- MAIN MENU ----------
def main_menu():
    pygame.mouse.set_visible(True)

    # Set up the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout Game - Menu")
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)

    # Buttons
    title = font.render("Breakout Game", True, WHITE)
    play_button = small_font.render("Play", True, BLUE)
    high_button = small_font.render("High Scores", True, (255, 215, 0))
    settings_button = small_font.render("Settings", True, (120, 200, 255))
    quit_button = small_font.render("Quit", True, RED)
    credits_button = small_font.render("Credits", True, (190, 60, 255))

    play_rect = play_button.get_rect(center=(SCREEN_WIDTH // 2, 300))
    high_rect = high_button.get_rect(center=(SCREEN_WIDTH // 2, 360))
    settings_rect = settings_button.get_rect(center=(SCREEN_WIDTH // 2, 420))
    credits_rect = credits_button.get_rect(center=(SCREEN_WIDTH // 2, 480))
    quit_rect = quit_button.get_rect(center=(SCREEN_WIDTH // 2, 540))

    hover_scale = {
        "play": 1.0,
        "high": 1.0,
        "settings": 1.0,
        "credits": 1.0,
        "quit": 1.0,
    }

    running = True
    while running:

        # Background
        if menu_background:
            screen.blit(pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        else:
            common.draw_gradient_background(screen, (20, 20, 60), (0, 0, 0))

        # UI Header
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        mouse_pos = pygame.mouse.get_pos()
        hover_any = False

        button_data = [
            ("play", play_button, play_rect),
            ("high", high_button, high_rect),
            ("settings", settings_button, settings_rect),
            ("credits", credits_button, credits_rect),
            ("quit", quit_button, quit_rect),
        ]

        for name, base_surf, base_rect in button_data:
            hovered = base_rect.collidepoint(mouse_pos)
            hover_any = hover_any or hovered

            # Smooth animation
            target = 1.25 if hovered else 1.0
            hover_scale[name] += (target - hover_scale[name]) * 0.15

            scale = hover_scale[name]
            scaled_w = int(base_surf.get_width() * scale)
            scaled_h = int(base_surf.get_height() * scale)
            scaled_surf = pygame.transform.smoothscale(base_surf, (scaled_w, scaled_h))
            scaled_rect = scaled_surf.get_rect(center=base_rect.center)

            # Glow effect behind button when hovered
            if hovered:
                glow_size = 10
                glow_surf = pygame.transform.smoothscale(
                    base_surf, (scaled_w + glow_size, scaled_h + glow_size)
                )
                glow_surf.set_alpha(120)
                glow_rect = glow_surf.get_rect(center=base_rect.center)
                screen.blit(glow_surf, glow_rect)

            screen.blit(scaled_surf, scaled_rect)

        # Cursor change on hover
        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_HAND if hover_any else pygame.SYSTEM_CURSOR_ARROW
        )

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    if menu_click_sound: menu_click_sound.play()
                    play_breakout(screen)

                elif high_rect.collidepoint(event.pos):
                    if menu_click_sound: menu_click_sound.play()
                    highscores.show_high_scores(screen)

                elif settings_rect.collidepoint(event.pos):
                    if menu_click_sound: menu_click_sound.play()
                    open_settings_menu(screen)

                elif credits_rect.collidepoint(event.pos):
                    if menu_click_sound: menu_click_sound.play()
                    show_credits(screen)

                elif quit_rect.collidepoint(event.pos):
                    if menu_click_sound: menu_click_sound.play()
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL:
                    open_test_menu(screen)
                elif event.key == pygame.K_SPACE:
                    if menu_click_sound: menu_click_sound.play()
                    play_breakout(screen)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        pygame.time.Clock().tick(60)


def open_settings_menu(screen):
    font = pygame.font.Font(None, 70)
    small = pygame.font.Font(None, 40)

    running = True

    # Settings list (label, key, unfinished_flag, special_note)
    options = [
        ("Tutorial", "tutorial_enabled", False, ""),
        ("Sound Volume", "sound_enabled", True, "(Not implemented)"),
        ("Music Volume", "music_enabled", True, "(Not implemented)"),
        ("Show FPS", "show_fps", True, "(Not fully implemented)"),
        ("Mouse Control", "mouse_enabled", True, "(Not implemented)"),
        ("Colorblind Mode", "colorblind_mode", True, "(Not implemented)")
    ]

    # Ensure all options exist in config
    for label, key, _, _ in options:
        config.setdefault(key, False)

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    # ---- COLUMN LAYOUT ----
    col_label_x = SCREEN_WIDTH // 2 - 310
    col_state_x = SCREEN_WIDTH // 2 - 50
    col_checkbox_x = SCREEN_WIDTH // 2 + 50
    col_note_x = SCREEN_WIDTH // 2 + 120

    start_y = 240
    spacing = 55

    # Build clickable rectangles for each row
    checkbox_rects = []

    for i, (_, key, _, _) in enumerate(options):
        checkbox = pygame.Rect(col_checkbox_x, start_y + i * spacing, 36, 36)
        checkbox_rects.append((checkbox, key))

    how_text = small.render("How to Play", True, WHITE)
    how_rect = how_text.get_rect(center=(SCREEN_WIDTH // 2, start_y + len(options) * spacing + 50))

    back_text = small.render("Back (ESC)", True, RED)
    back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))

    while running:
        screen.fill((20, 20, 20))

        title = font.render("SETTINGS", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # -------- DRAW SETTINGS --------
        for i, (label, key, unfinished, note) in enumerate(options):
            y = start_y + i * spacing

            # Setting name
            txt = small.render(label, True, WHITE)
            screen.blit(txt, (col_label_x, y))

            # State ON/OFF color
            state = "ON" if config.get(key) else "OFF"
            color = GREEN if state == "ON" else RED

            state_text = small.render(state, True, color)
            screen.blit(state_text, (col_state_x, y))

            # Checkbox
            checkbox, key_ref = checkbox_rects[i]
            pygame.draw.rect(screen, WHITE, checkbox, 3)
            if config.get(key):
                pygame.draw.line(screen, WHITE, (checkbox.left + 7, checkbox.centery),
                                (checkbox.centerx, checkbox.bottom - 7), 4)
                pygame.draw.line(screen, WHITE, (checkbox.centerx, checkbox.bottom - 7),
                                (checkbox.right - 7, checkbox.top + 7), 4)

            if unfinished:
                note_text = small.render(note, True, (180, 180, 180))
                screen.blit(note_text, (col_note_x, y))

        # Bottom buttons
        screen.blit(how_text, how_rect)
        screen.blit(back_text, back_rect)

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                for (checkbox, key) in checkbox_rects:
                    if checkbox.collidepoint(pos):
                        config[key] = not config[key]
                        with open("config.json", "w") as f:
                            json.dump(config, f, indent=2)

                if how_rect.collidepoint(pos):
                    show_how_to_play(screen)

                if back_rect.collidepoint(pos):
                    return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# ---------- HOW TO PLAY ----------
def show_how_to_play(screen):
    font = pygame.font.Font(None, 60)
    small = pygame.font.Font(None, 36)

    running = True
    while running:
        screen.fill((0, 0, 0))

        title = font.render("HOW TO PLAY", True, (255, 255, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        lines = [
            "Use the SPACE bar to launch the ball on a new life.",
            "Use the arrow keys or A/D to move the paddle.",
            "Bounce the ball to break all the blocks.",
            "You have 3 lives. The game ends when they run out.",
            "Press ESC to pause the game.",
        ]

        y = 260
        for line in lines:
            txt = small.render(line, True, WHITE)
            screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y))
            y += 50

        back = small.render("Press ESC to return", True, RED)
        screen.blit(back, (SCREEN_WIDTH // 2 - back.get_width() // 2, 550))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# ---------- CREDITS ----------
def show_credits(screen):
    font = pygame.font.Font(None, 60)
    small = pygame.font.Font(None, 40)

    running = True
    while running:
        screen.fill((0, 0, 0))

        # ESC at the top center
        esc = small.render("Press ESC to return", True, RED)
        esc_rect = esc.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(esc, esc_rect)

        # Credits title — 40px below ESC
        title = font.render("CREDITS", True, (255, 255, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, esc_rect.bottom + 40))
        screen.blit(title, title_rect)

        # Main credits block starts below the title
        start_y = title_rect.bottom + 40

        names = [
            "Program Manager / Team Lead:",
            "• Christopher Lehn",

            "Gameplay Developer – Dustyn Hermann",
            "Core Systems Developer – Joshua Marshall",

            "UI/UX & Art–Audio Designer:",
            "• Venus Gilyard",

            "Documentation & Quality Tester:",
            "• Manuel Delgado",

            "---------------------------------------------",
            "Special Thanks:",
            "• Everyone who tested the game",
            "---------------------------------------------",

            "Course Acknowledgments:",
            "• University of Maryland Global Campus (UMGC)",
            "• Professor Jeff Sanford – Primary Instructor, CMSC 495",
            "   Thank you for your guidance and support!"
        ]

        y = start_y
        spacing = 45

        for line in names:
            txt = small.render(line, True, WHITE)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH // 2, y))
            screen.blit(txt, txt_rect)
            y += spacing

        # ---------- Exit event ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# ---------- DEBUG MENU ----------
def open_test_menu(screen):
    font = pygame.font.Font(None, 60)
    small = pygame.font.Font(None, 36)

    running = True
    while running:
        screen.fill((0, 0, 0))

        title = font.render("TEST MODE", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        options = [
            "1 - Regular Debug (1 Block)",
            "2 - Countdown Timer Test",
            "3 - Start at Level 1",
            "4 - Start at Level 2",
            "5 - Start at Level 3",
            "6 - Start at Level 4",
            "7 - Start at Level 5",
            "ESC - Return to Menu"
        ]

        y = 260
        for line in options:
            txt = small.render(line, True, WHITE)
            screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y))
            y += 50

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_1: return play_breakout(screen, "one_block")
                if key == pygame.K_2: return play_breakout(screen, "countdown")
                if key == pygame.K_3: return play_breakout(screen, "level_1")
                if key == pygame.K_4: return play_breakout(screen, "level_2")
                if key == pygame.K_5: return play_breakout(screen, "level_3")
                if key == pygame.K_6: return play_breakout(screen, "level_4")
                if key == pygame.K_7: return play_breakout(screen, "level_5")
                if key == pygame.K_ESCAPE: return

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# ---------- GAME LAUNCHER ----------
def play_breakout(screen, debug_mode=False):
    replay = True
    while replay:
        replay = breakout.play(screen, debug_mode)
        pygame.mouse.set_visible(True)
    main_menu()


# ---------- ENTRY ----------
if __name__ == '__main__':
    pygame.init()
    main_menu()
