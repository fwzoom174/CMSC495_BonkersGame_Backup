import sys
import pygame
import common
import os
import json

from common import RED, WHITE, GREEN, BLUE, SCREEN_WIDTH, SCREEN_HEIGHT, ROOT_PATH
from scenes import breakout, highscores
from scenes.loading import show_loading_screen

# Initialize pygame FIRST
pygame.init()
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

def save_config():
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except:
        print("Warning: Could not save config.json")

def current_sfx_volume():
    try:
        with open(config_path, "r") as f:
            cfg_local = json.load(f)
        level = cfg_local.get("sound_volume", 5)
        try:
            level = int(level)
        except:
            level = 5
        level = max(0, min(5, level))
        return level / 5.0
    except:
        return 1.0
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)

    # ensure key exists
    config.setdefault("tutorial_enabled", True)
    config.setdefault("sound_volume", 5)
    config.setdefault("music_volume", 5)
    config.setdefault("show_fps", False)
    config.setdefault("mouse_enabled", False)

else:
    config = {
        "tutorial_enabled": True
    }

    # --- Settings defaults ---
    config.setdefault("sound_volume", 5)
    config.setdefault("music_volume", 5)
    config.setdefault("show_fps", False)
    config.setdefault("mouse_enabled", False)

    save_config()

# Character selection setup (Global)
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



# ---------- MAIN MENU ----------
def main_menu():
    pygame.mouse.set_visible(True)

    from common import menu_music, gameplay_music, boss_music, apply_music_volume
    gameplay_music.stop()
    boss_music.stop()
    menu_music.play(loops=-1)
    apply_music_volume(config.get("music_volume", 5))

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

    # fallback title text if image fails
    title = font.render("Breakout Game", True, WHITE)

    # Button positions 
    button_x = 190
    button_start_y = 300
    button_spacing = 80
    
    play_rect = pygame.Rect(button_x, button_start_y, 300, 60)
    high_rect = pygame.Rect(button_x, button_start_y + button_spacing, 300, 60)
    settings_rect = pygame.Rect(button_x, button_start_y + button_spacing * 2, 300, 60)
    credits_rect = pygame.Rect(button_x, button_start_y + button_spacing * 3, 300, 60)
    quit_rect = pygame.Rect(button_x, button_start_y + button_spacing * 4, 300, 60)
    
    selected_character = config.get("last_character", 0)

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
        left_arrow = pygame.image.load("media/graphics/items/left arrow.png")
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
                hovered = button_rect.collidepoint(mouse_pos)
                hover_any = hover_any or hovered
                
                # Smooth scale animation on hover
                target = 1.1 if hovered else 1.0
                hover_scale[name] += (target - hover_scale[name]) * 0.15
                
                scale = hover_scale[name]
                if scale != 1.0:
                    # Scale the button
                    scaled_w = int(button_img.get_width() * scale)
                    scaled_h = int(button_img.get_height() * scale)
                    scaled_img = pygame.transform.smoothscale(button_img, (scaled_w, scaled_h))
                    scaled_rect = scaled_img.get_rect(center=button_rect.center)
                    screen.blit(scaled_img, scaled_rect)
                else:
                    # Draw normal size
                    screen.blit(button_img, button_rect)    

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
                    if menu_click_sound and current_sfx_volume() > 0:
                        menu_click_sound.set_volume(current_sfx_volume())
                        menu_click_sound.play()
                    # Pass the selected character image to the game
                    selected_char_image = characters[selected_character]["image"]
                    play_breakout(screen, selected_char_image)

                elif high_rect.collidepoint(event.pos):
                    if menu_click_sound and current_sfx_volume() > 0:
                        menu_click_sound.set_volume(current_sfx_volume())
                        menu_click_sound.play()
                    highscores.show_high_scores(screen)

                elif settings_rect.collidepoint(event.pos):
                    if menu_click_sound and current_sfx_volume() > 0:
                        menu_click_sound.set_volume(current_sfx_volume())
                        menu_click_sound.play()
                    open_settings_menu(screen)

                elif credits_rect.collidepoint(event.pos):
                    if menu_click_sound and current_sfx_volume() > 0:
                        menu_click_sound.set_volume(current_sfx_volume())
                        menu_click_sound.play()
                    show_credits(screen)

                elif quit_rect.collidepoint(event.pos):
                    if menu_click_sound and current_sfx_volume() > 0:
                        menu_click_sound.set_volume(current_sfx_volume())
                        menu_click_sound.play()
                    pygame.quit()
                    sys.exit()

                # Arrow click handling
                # Left arrow - go to previous character
                elif selected_character > 0:  
                    left_arrow_rect = pygame.Rect(select_x - 40, select_y + 120, 40, 40)
                    if left_arrow_rect.collidepoint(event.pos):
                        if menu_click_sound and current_sfx_volume() > 0:
                            menu_click_sound.set_volume(current_sfx_volume())
                            menu_click_sound.play()
                        selected_character -= 1
                        #Save to config 
                        config["last_character"] = selected_character
                        save_config()
                
                # Right arrow - go to next character
                if selected_character < len(characters) - 1:  
                    right_arrow_rect = pygame.Rect(select_x + 250, select_y + 120, 40, 40)
                    if right_arrow_rect.collidepoint(event.pos):
                        if menu_click_sound and current_sfx_volume() > 0:
                            menu_click_sound.set_volume(current_sfx_volume())
                            menu_click_sound.play()
                        selected_character += 1
                        #Save to config 
                        config["last_character"] = selected_character
                        save_config()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL:
                    open_test_menu(screen)
                elif event.key == pygame.K_SPACE:
                    if menu_click_sound and current_sfx_volume() > 0:
                        menu_click_sound.set_volume(current_sfx_volume())
                        menu_click_sound.play()
                    selected_char_image = characters[selected_character]["image"]
                    play_breakout(screen, selected_char_image)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        pygame.time.Clock().tick(60)


def open_settings_menu(screen):
    font_path = os.path.join(ROOT_PATH, "media", "graphics", "font", "Pixeboy.ttf")
    font = pygame.font.Font(font_path, 70)
    small = pygame.font.Font(font_path, 40)

    label_colors = [
        (0, 255, 255),
        (255, 105, 180),
        (255, 255, 0),
        (255, 120, 60)
    ]

    running = True

    # Settings list
    options = [
        ("Tutorial", "tutorial_enabled", False, ""),
        ("Sound Volume", "sound_volume", True, ""),
        ("Music Volume", "music_volume", True, ""),
        ("Show FPS", "show_fps", True, ""),
        ("Mouse Control", "mouse_enabled", True, ""),
    ]

    # Ensure all options exist in config
    for label, key, _, _ in options:
        if "volume" in key:
            config.setdefault(key, 5)
        else:
            config.setdefault(key, False)

    save_config()

    # ---- COLUMN LAYOUT ----
    col_label_x = SCREEN_WIDTH // 2 - 330
    col_state_x = SCREEN_WIDTH // 2 - 40
    col_checkbox_x = SCREEN_WIDTH // 2 + 80
    col_note_x = SCREEN_WIDTH // 2 + 260

    start_y = 240
    spacing = 55

    # Build clickable rectangles for each row
    checkbox_rects = []

    volume_minus_rects = {}
    volume_plus_rects = {}
    volume_value_rects = {}

    value_box_width = 60

    for i, (label, key, unfinished, note) in enumerate(options):
        y = start_y + i * spacing

        # Sound Volume row
        if label == "Sound Volume":
            value_rect = pygame.Rect(col_checkbox_x - value_box_width // 2, y + 4, value_box_width, 40)
            minus_rect = pygame.Rect(value_rect.left - 50, y + 4, 40, 40)
            plus_rect = pygame.Rect(value_rect.right + 10, y + 4, 40, 40)

            volume_minus_rects["sound_volume"] = minus_rect
            volume_plus_rects["sound_volume"] = plus_rect
            volume_value_rects["sound_volume"] = value_rect
            checkbox_rects.append((None, key))
            continue

        # Music Volume row
        if label == "Music Volume":
            value_rect = pygame.Rect(col_checkbox_x - value_box_width // 2, y + 4, value_box_width, 40)
            minus_rect = pygame.Rect(value_rect.left - 50, y + 4, 40, 40)
            plus_rect = pygame.Rect(value_rect.right + 10, y + 4, 40, 40)

            volume_minus_rects["music_volume"] = minus_rect
            volume_plus_rects["music_volume"] = plus_rect
            volume_value_rects["music_volume"] = value_rect
            checkbox_rects.append((None, key))
            continue

        # Normal checkbox rows
        checkbox = pygame.Rect(col_checkbox_x - 18, y + 4, 36, 36)
        checkbox_rects.append((checkbox, key))

    how_text = small.render("How to Play", True, WHITE)
    how_rect = how_text.get_rect(center=(SCREEN_WIDTH // 2, start_y + len(options) * spacing + 50))

    back_text = small.render("Back (ESC)", True, RED)
    back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))

    while running:
        from scenes.win_lose import draw_retro_background
        draw_retro_background(screen)

        title = font.render("SETTINGS", True, (255, 255, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # -------- DRAW SETTINGS --------
        for i, (label, key, unfinished, note) in enumerate(options):
            y = start_y + i * spacing

            # Setting name
            txt = small.render(label, True, label_colors[i % len(label_colors)])
            screen.blit(txt, (col_label_x, y))

            # State ON/OFF color
            state = "ON" if config.get(key) else "OFF"
            # ----- DRAW VOLUME CONTROLS -----
            if label == "Sound Volume":
                minus = volume_minus_rects["sound_volume"]
                plus = volume_plus_rects["sound_volume"]
                value = volume_value_rects["sound_volume"]

                pygame.draw.rect(screen, WHITE, minus, 3)
                pygame.draw.rect(screen, WHITE, plus, 3)
                pygame.draw.rect(screen, WHITE, value, 3)

                minus_text = small.render("-", True, WHITE)
                plus_text = small.render("+", True, WHITE)

                val = str(config.get("sound_volume", 5))
                val_surf = small.render(val, True, WHITE)
                val_rect = val_surf.get_rect(center=value.center)

                screen.blit(val_surf, val_rect)
                screen.blit(minus_text, minus.move(10, 5))
                screen.blit(plus_text, plus.move(10, 5))

                continue

            if label == "Music Volume":
                minus = volume_minus_rects["music_volume"]
                plus = volume_plus_rects["music_volume"]
                value = volume_value_rects["music_volume"]

                pygame.draw.rect(screen, WHITE, minus, 3)
                pygame.draw.rect(screen, WHITE, plus, 3)
                pygame.draw.rect(screen, WHITE, value, 3)

                minus_text = small.render("-", True, WHITE)
                plus_text = small.render("+", True, WHITE)

                val = str(config.get("music_volume", 5))
                val_surf = small.render(val, True, WHITE)
                val_rect = val_surf.get_rect(center=value.center)

                screen.blit(val_surf, val_rect)
                screen.blit(minus_text, minus.move(10, 5))
                screen.blit(plus_text, plus.move(10, 5))

                continue

            color = GREEN if state == "ON" else RED

            state_text = small.render(state, True, color)
            screen.blit(state_text, (col_state_x, y))

            # Checkbox
            checkbox, key_ref = checkbox_rects[i]
            pygame.draw.rect(screen, WHITE, checkbox, 3)
            if config.get(key):
                pygame.draw.line(screen, (255, 255, 0),
                                 (checkbox.left + 6, checkbox.top + 6),
                                 (checkbox.right - 6, checkbox.bottom - 6), 4)
                pygame.draw.line(screen, (255, 255, 0),
                                 (checkbox.right - 6, checkbox.top + 6),
                                 (checkbox.left + 6, checkbox.bottom - 6), 4)

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

                # ------ Volume Buttons ------
                if "sound_volume" in volume_minus_rects:
                    if volume_minus_rects["sound_volume"].collidepoint(pos):
                        config["sound_volume"] = max(0, config.get("sound_volume", 5) - 1)
                        save_config()
                        if menu_click_sound:
                            menu_click_sound.set_volume(current_sfx_volume())
                        try:
                            breakout.apply_sound_volumes()
                        except:
                            pass

                    if volume_plus_rects["sound_volume"].collidepoint(pos):
                        config["sound_volume"] = min(5, config.get("sound_volume", 5) + 1)
                        save_config()
                        if menu_click_sound:
                            menu_click_sound.set_volume(current_sfx_volume())
                        try:
                            breakout.apply_sound_volumes()
                        except:
                            pass

                if "music_volume" in volume_minus_rects:
                    if volume_minus_rects["music_volume"].collidepoint(pos):
                        config["music_volume"] = max(0, config.get("music_volume", 5) - 1)
                        save_config()
                        from common import apply_music_volume
                        apply_music_volume(config["music_volume"])

                    if volume_plus_rects["music_volume"].collidepoint(pos):
                        config["music_volume"] = min(5, config.get("music_volume", 5) + 1)
                        save_config()
                        from common import apply_music_volume
                        apply_music_volume(config["music_volume"])

                for (checkbox, key) in checkbox_rects:
                    if checkbox and checkbox.collidepoint(pos):
                        config[key] = not config[key]
                        save_config()

                if how_rect.collidepoint(pos):
                    show_how_to_play(screen)

                if back_rect.collidepoint(pos):
                    if menu_click_sound and current_sfx_volume() > 0:
                        menu_click_sound.set_volume(current_sfx_volume())
                        menu_click_sound.play()
                    return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if menu_click_sound and current_sfx_volume() > 0:
                    menu_click_sound.set_volume(current_sfx_volume())
                    menu_click_sound.play()
                return

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# ---------- HOW TO PLAY ----------
def show_how_to_play(screen):
    font = pygame.font.Font(None, 60)
    small = pygame.font.Font(None, 36)

    running = True
    while running:
        from scenes.win_lose import draw_retro_background

        draw_retro_background(screen)

        title = font.render("HOW TO PLAY", True, (255, 255, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        underline_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 200,
            150 + title.get_height() + 10,
            400,
            4
        )
        pygame.draw.rect(screen, (0, 255, 255), underline_rect)

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
                if menu_click_sound and current_sfx_volume() > 0:
                    menu_click_sound.set_volume(current_sfx_volume())
                    menu_click_sound.play()
                return

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# ---------- CREDITS ----------
def show_credits(screen):
    font = pygame.font.Font(None, 60)
    small = pygame.font.Font(None, 40)

    running = True
    while running:
        from scenes.win_lose import draw_retro_background

        draw_retro_background(screen)

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
                if menu_click_sound and current_sfx_volume() > 0:
                    menu_click_sound.set_volume(current_sfx_volume())
                    menu_click_sound.play()
                return

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# ---------- DEBUG MENU ----------
def open_test_menu(screen):
    font = pygame.font.Font(None, 60)
    small = pygame.font.Font(None, 36)

    running = True
    while running:
        from common import draw_gradient_background
        from scenes.win_lose import draw_retro_background

        draw_retro_background(screen)

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
                if key == pygame.K_1: return play_breakout(screen, characters[0]["image"], debug_mode="one_block")
                if key == pygame.K_2: return play_breakout(screen, characters[0]["image"], debug_mode="countdown")
                if key == pygame.K_3: return play_breakout(screen, characters[0]["image"], debug_mode="level_1")
                if key == pygame.K_4: return play_breakout(screen, characters[0]["image"], debug_mode="level_2")
                if key == pygame.K_5: return play_breakout(screen, characters[0]["image"], debug_mode="level_3")
                if key == pygame.K_6: return play_breakout(screen, characters[0]["image"], debug_mode="level_4")
                if key == pygame.K_7: return play_breakout(screen, characters[0]["image"], debug_mode="level_5")
                if key == pygame.K_ESCAPE: return

        pygame.display.flip()
        pygame.time.Clock().tick(60)


# ---------- GAME LAUNCHER ----------
def play_breakout(screen, character_image=None, debug_mode=False):
    from common import menu_music, gameplay_music, boss_music, apply_music_volume

    menu_music.stop()
    boss_music.stop()
    gameplay_music.play(loops=-1)
    apply_music_volume(config.get("music_volume", 5))

    replay = True
    while replay:
        replay = breakout.play(screen, debug_mode, character_image)
        pygame.mouse.set_visible(True)
    main_menu()


# ---------- ENTRY ----------
if __name__ == '__main__':
    main_menu()