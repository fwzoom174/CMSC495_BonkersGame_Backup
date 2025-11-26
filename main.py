import sys
import pygame
import common
import os
import json

from common import RED, WHITE, GREEN, BLUE, SCREEN_WIDTH, SCREEN_HEIGHT
from scenes import breakout, highscores
from scenes.loading import show_loading_screen

# Initialize pygame FIRST
pygame.init()
pygame.mixer.init()

try:
    menu_click_sound = pygame.mixer.Sound("media/audio/media_audio_selection_click.wav")
except:
    print("Warning: Could not load menu click sound.")
    menu_click_sound = None

try:
    menu_background = pygame.image.load("media/graphics/background/back-landscape-grid.png")
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

    # Load title image
    try:
        title_image = pygame.image.load("media/graphics/items/breakout-game-title.png")
        title_image = pygame.transform.scale(title_image, (400, 100))
    except:
        print("Warning: Could not load title image.")
        title_image = None

    # Load button images
    try:
        play_button_img = pygame.image.load("media/graphics/items/play-button.png")
        highscores_button_img = pygame.image.load("media/graphics/items/highscores-button.png")
        settings_button_img = pygame.image.load("media/graphics/items/settings-button.png")
        credits_button_img = pygame.image.load("media/graphics/items/credits-button.png")
        quit_button_img = pygame.image.load("media/graphics/items/quit-button.png")
        
        # Scale buttons to consistent size (adjust if needed)
        button_width = 300
        button_height = 60
        play_button_img = pygame.transform.scale(play_button_img, (button_width, button_height))
        highscores_button_img = pygame.transform.scale(highscores_button_img, (button_width, button_height))
        settings_button_img = pygame.transform.scale(settings_button_img, (button_width, button_height))
        credits_button_img = pygame.transform.scale(credits_button_img, (button_width, button_height))
        quit_button_img = pygame.transform.scale(quit_button_img, (button_width, button_height))
    except Exception as e:
        print(f"Warning: Could not load button images: {e}")
        # Fallback to text buttons if images don't load
        play_button_img = None

    # Set up the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout Game - Menu")
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)
    show_loading_screen(screen, font)

    # Button positions 
    button_x = 190
    button_start_y = 300
    button_spacing = 80
    
    play_rect = pygame.Rect(button_x, button_start_y, 300, 60)
    high_rect = pygame.Rect(button_x, button_start_y + button_spacing, 300, 60)
    settings_rect = pygame.Rect(button_x, button_start_y + button_spacing * 2, 300, 60)
    credits_rect = pygame.Rect(button_x, button_start_y + button_spacing * 3, 300, 60)
    quit_rect = pygame.Rect(button_x, button_start_y + button_spacing * 4, 300, 60)
    
    # Character selection setup 
    characters = [
        {"name": "BALL", "image": "media/graphics/balls_characters/ball.png"},
        {"name": "CRYSTAL", "image": "media/graphics/balls_characters/crystal.png"},
        {"name": "GHOST 1", "image": "media/graphics/balls_characters/ghost 1.png"},
        {"name": "GHOST 2", "image": "media/graphics/balls_characters/ghost 2.png"},
        {"name": "JEFF", "image": "media/graphics/balls_characters/jeff.png"},
        {"name": "PAC 1", "image": "media/graphics/balls_characters/Pac-1.png"},
        {"name": "PAC 2", "image": "media/graphics/balls_characters/Pac-2.png"},
        {"name": "STEVE", "image": "media/graphics/balls_characters/steve.png"},
    ]
    
    selected_character = 0
    
    character_images = []
    for char in characters:
        try:
            img = pygame.image.load(char["image"])
            img = pygame.transform.scale(img, (100, 100))
            character_images.append(img)
        except Exception as e:
            print(f"Warning: Could not load {char['name']}: {e}")
            character_images.append(None)
    
    try:
        select_player_img = pygame.image.load("media/graphics/items/select-player.png")
        select_player_img = pygame.transform.scale(select_player_img, (300, 60))
    except:
        print("Warning: Could not load select-player.png")
        select_player_img = None

    # Load arrow images
    try:
        left_arrow = pygame.image.load("media/graphics/items/left arrow .png")
        left_arrow_dark = pygame.image.load("media/graphics/items/left-arrow-dark.png")
        right_arrow = pygame.image.load("media/graphics/items/right-arrow.png")
        right_arrow_dark = pygame.image.load("media/graphics/items/right-arrow-dark.png")
        
        # Scale light arrows
        arrow_size = (40, 40)
        left_arrow = pygame.transform.scale(left_arrow, arrow_size)
        right_arrow = pygame.transform.scale(right_arrow, arrow_size)
        
        # Scale dark arrows 
        dark_arrow_size = (40, 40) 
        left_arrow_dark = pygame.transform.scale(left_arrow_dark, dark_arrow_size)
        right_arrow_dark = pygame.transform.scale(right_arrow_dark, dark_arrow_size)
    except Exception as e:
        print(f"Warning: Could not load arrow images: {e}")
        left_arrow = None
    
    
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

            # Draw BREAKOUT title image
        if title_image:
            title_x = 150
            title_y = 130
            screen.blit(title_image, (title_x, title_y))
        else:
            # Fallback if image doesn't load
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        mouse_pos = pygame.mouse.get_pos()
        hover_any = False

    # Draw buttons with images
        button_data = [
            ("play", play_button_img, play_rect),
            ("high", highscores_button_img, high_rect),
            ("settings", settings_button_img, settings_rect),
            ("credits", credits_button_img, credits_rect),
            ("quit", quit_button_img, quit_rect),
        ]

        for name, button_img, button_rect in button_data:
            if button_img:
                # Draw the button image
                screen.blit(button_img, button_rect)
                
                # Check if hovered for cursor change
                if button_rect.collidepoint(mouse_pos):
                    hover_any = True

        # Draw "Select Player" section (right side)
        select_x = SCREEN_WIDTH - 450
        select_y = 350
        
        # Draw "Select Player" image/title (smaller)
        if select_player_img:
            smaller_select = pygame.transform.scale(select_player_img, (250, 50))
            screen.blit(smaller_select, (select_x, select_y))
            title_width = 250  # Width of the select player image
        
        # Draw character NAME centered under "Select Player" title
        try:
            name_font = pygame.font.Font("media/graphics/font/Pixeboy.ttf", 36)
        except:
            name_font = pygame.font.Font(None, 36)
        character_name = name_font.render(characters[selected_character]["name"], True, (100, 200, 255))
        name_x = select_x + (title_width // 2) - (character_name.get_width() // 2)  # Center it
        screen.blit(character_name, (name_x, select_y + 70))
        
        # Draw character image SMALLER and centered under the name
        if character_images[selected_character]:
            # Make character smaller
            small_char = pygame.transform.scale(character_images[selected_character], (60, 60))  # Smaller!
            char_img_x = select_x + (title_width // 2) - 30  # Center it (half of 60)
            char_img_y = select_y + 130
            screen.blit(small_char, (char_img_x, char_img_y))

        # Draw arrows (already scaled at load time)
        arrow_y = select_y + 135
        
        # Left arrow position
        left_arrow_x = select_x - 40
        
        # Right arrow position
        right_arrow_x = select_x + 250
        
        # Left arrow (dark if on first character)
        if selected_character == 0:
            if left_arrow_dark:
                screen.blit(left_arrow_dark, (left_arrow_x, arrow_y))
        else:
            if left_arrow:
                screen.blit(left_arrow, (left_arrow_x, arrow_y))
        
        # Right arrow (dark if on last character)
        if selected_character == len(characters) - 1:
            if right_arrow_dark:
                screen.blit(right_arrow_dark, (right_arrow_x, arrow_y))
        else:
            if right_arrow:
                screen.blit(right_arrow, (right_arrow_x, arrow_y))
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
                    # Pass the selected character image to the game
                    selected_char_image = characters[selected_character]["image"]
                    play_breakout(screen, selected_char_image)

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

                # Arrow click handling
                # Left arrow - go to previous character
                elif selected_character > 0:  
                    left_arrow_rect = pygame.Rect(select_x - 40, select_y + 120, 40, 40)
                    if left_arrow_rect.collidepoint(event.pos):
                        if menu_click_sound: menu_click_sound.play()
                        selected_character -= 1
                
                # Right arrow - go to next character
                if selected_character < len(characters) - 1:  
                    right_arrow_rect = pygame.Rect(select_x + 250, select_y + 120, 40, 40)
                    if right_arrow_rect.collidepoint(event.pos):
                        if menu_click_sound: menu_click_sound.play()
                        selected_character += 1

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
                if key == pygame.K_1: return play_breakout(screen, debug_mode="one_block")
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
def play_breakout(screen, character_image=None, debug_mode=False):
    replay = True
    while replay:
        replay = breakout.play(screen, debug_mode, character_image)
        pygame.mouse.set_visible(True)
    main_menu()


# ---------- ENTRY ----------
if __name__ == '__main__':
    main_menu()