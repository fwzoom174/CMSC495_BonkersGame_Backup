import pygame
import sys
import os
import json
from common import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, RED, ORANGE, ROOT_PATH

# Initialize Pygame
pygame.init()

pygame.mixer.init()

# Load game over sound
try:
    game_over_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, "media", "audio", "media_audio_game_over.wav"))
    win_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, "media", "audio", "media_audio_win.wav"))
    menu_click_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, "media", "audio", "media_audio_selection_click.wav"))

except:
    print("Warning: Could not load game over sound.")
    game_over_sound = None
    win_sound = None
    menu_click_sound = None

# Colors
BLUE = (18, 89, 202)
YELLOW = (254, 175, 54)

config_path = "config.json"

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

# ---------- FONT & GRAPHICS UTILITIES ----------
def load_custom_font(size, bold=False):
    font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
    return pygame.font.Font(font_path, size)

def draw_retro_background(screen):
    background = pygame.image.load(os.path.join(ROOT_PATH, 'media', 'graphics', 'background', 'back-grid.png'))
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(background, (0, 0))

# ---------- DRAWING FUNCTIONS ----------
def draw_button(screen, text, font, center_pos, selected=False):
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=center_pos)

    #Buttons, Padding for Height
    button_width = 180
    padding_y = 15
    button_height = text_rect.height + padding_y * 2

    # Top-left corner of button
    x = center_pos[0] - button_width // 2
    y = text_rect.top - padding_y

    # Border color changes if selected
    border_color = BLUE if selected else ORANGE
    border_width = 6

    # Pixelated rounded corners
    corner_size = 20

    # Main body borders
    # Top border (with corner cuts)
    pygame.draw.rect(screen, border_color, (x + corner_size, y, button_width - corner_size * 2, border_width))
    # Bottom border (with corner cuts)
    pygame.draw.rect(screen, border_color, (x + corner_size, y + button_height - border_width, button_width - corner_size * 2, border_width))
    # Left border (with corner cuts)
    pygame.draw.rect(screen, border_color, (x, y + corner_size, border_width, button_height - corner_size * 2))
    # Right border (with corner cuts)
    pygame.draw.rect(screen, border_color, (x + button_width - border_width, y + corner_size, border_width, button_height - corner_size * 2))

    # Corner Piece
    corner_block = 8

    # Top-left corner
    pygame.draw.rect(screen, border_color, (x + corner_block, y + corner_block, border_width, border_width))

    # Top-right corner
    pygame.draw.rect(screen, border_color, (x + button_width - corner_block - border_width, y + corner_block, border_width, border_width))

    # Bottom-left corner
    pygame.draw.rect(screen, border_color, (x + corner_block, y + button_height - corner_block - border_width, border_width, border_width))

    # Bottom-right corner
    pygame.draw.rect(screen, border_color, (x + button_width - corner_block - border_width, y + button_height - corner_block - border_width, border_width, border_width))

    # Fill inside
    inner_rect = pygame.Rect(x + border_width, y + border_width, button_width - border_width * 2, button_height - border_width * 2)
    pygame.draw.rect(screen, BLACK, inner_rect)

    # Draw text centered
    text_rect.center = center_pos
    screen.blit(text_surface, text_rect)
    return text_rect

def draw_animated_text(screen, full_text, letter_states, font, color, center_pos):
    x_offset = 0

    # Calculate total width to center the text
    temp_surface = font.render(full_text, True, color)
    total_width = temp_surface.get_width()
    start_x = center_pos[0] - total_width // 2

    for i, char in enumerate(full_text):
        if i < len(letter_states):
            # Animation Progress
            progress = letter_states[i]

            if progress > 0:
                # Render the letter
                letter_surface = font.render(char, True, color)

                # Smooth fade-in effect
                alpha = int(255 * min(progress, 1.0))
                letter_surface.set_alpha(alpha)

                # Smooth bounce/scale effect
                if progress < 1.0:
                    scale = 1.0 + (1.0 - progress) * 0.3
                    scaled_width = int(letter_surface.get_width() * scale)
                    scaled_height = int(letter_surface.get_height() * scale)
                    letter_surface = pygame.transform.scale(letter_surface, (scaled_width, scaled_height))

                # Position and draw
                letter_rect = letter_surface.get_rect()
                letter_rect.centerx = start_x + x_offset + letter_rect.width // 2
                letter_rect.centery = center_pos[1]
                screen.blit(letter_surface, letter_rect)

        # Move offset for next letter
        char_width = font.render(char, True, color).get_width()
        x_offset += char_width

# ---------- HELPER FUNCTIONS ----------
def get_player_initials(screen, score):
    initials = ""
    max_letters = 3
    entering_name = True

    while entering_name:
        draw_retro_background(screen)
        score_text = load_custom_font(40).render(f"SCORE: {score}", True, BLUE)
        screen.blit(score_text, score_text.get_rect(centerx=SCREEN_WIDTH // 2, top=100))
        title = load_custom_font(90).render("ENTER INITIALS", True, YELLOW)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)))
        initials_display = load_custom_font(100).render(initials or "_", True, WHITE)
        screen.blit(initials_display, initials_display.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        hint = load_custom_font(40).render("Press ENTER when done", True, ORANGE)
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120)))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                vol = current_sfx_volume()
                if menu_click_sound and vol > 0:
                    menu_click_sound.set_volume(vol)
                    menu_click_sound.play()
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and initials:
                    entering_name = False
                elif ev.key == pygame.K_BACKSPACE:
                    initials = initials[:-1]
                elif pygame.K_a <= ev.key <= pygame.K_z and len(initials) < max_letters:
                    initials += chr(ev.key).upper()

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    return initials

def end_screen(screen, win=True, score=500):
    pygame.mouse.set_visible(True)
    pygame.display.set_caption("Congratulations!" if win else "Game Over")

    vol = current_sfx_volume()

    if win and win_sound and vol > 0:
        win_sound.set_volume(vol)
        win_sound.play()
    elif not win and game_over_sound and vol > 0:
        game_over_sound.set_volume(vol)
        game_over_sound.play()

    full_text = "YOU WIN!" if win else "GAME OVER"
    text_color = YELLOW if win else RED

    selected = "YES"
    yes_button, no_button = None, None
    game_font = load_custom_font(150)

    letter_states = []
    letter_delay = 40
    animation_speed = 0.15
    last_letter_time = pygame.time.get_ticks()
    typewriter_done = False

    buttons_alpha = 0
    buttons_fade_speed = 40

    running = True
    initials = ""

    while running:
        draw_retro_background(screen)

        score_text = load_custom_font(40).render(f"SCORE: {score}", True, BLUE)
        score_rect = score_text.get_rect(centerx=SCREEN_WIDTH // 2, top=100)
        screen.blit(score_text, score_rect)

        current_time = pygame.time.get_ticks()

        if len(letter_states) < len(full_text) and current_time - last_letter_time > letter_delay:
            letter_states.append(0.0)
            last_letter_time = current_time

        for i in range(len(letter_states)):
            if letter_states[i] < 1.0:
                letter_states[i] += animation_speed
                if letter_states[i] > 1.0:
                    letter_states[i] = 1.0

        if len(letter_states) == len(full_text) and all(s >= 1.0 for s in letter_states):
            typewriter_done = True
            if buttons_alpha < 255:
                buttons_alpha += buttons_fade_speed
                if buttons_alpha > 255:
                    buttons_alpha = 255

        draw_animated_text(screen, full_text, letter_states, game_font, text_color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))

        if typewriter_done and not initials:
            initials = get_player_initials(screen, score)

        if typewriter_done and initials:
            instruction_text = load_custom_font(48).render("Play Again?", True, WHITE)
            instruction_text.set_alpha(buttons_alpha)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            screen.blit(instruction_text, instruction_rect)

            font = load_custom_font(48)
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            yes_button = draw_button(temp_surface, "YES", font, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100), selected == "YES")
            no_button = draw_button(temp_surface, "NO", font, (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 + 100), selected == "NO")
            temp_surface.set_alpha(buttons_alpha)
            screen.blit(temp_surface, (0, 0))

        # --- Cursor control (changes only over buttons) ---
        mouse_pos = pygame.mouse.get_pos()
        if (yes_button and yes_button.collidepoint(mouse_pos)) or (no_button and no_button.collidepoint(mouse_pos)):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not typewriter_done or buttons_alpha < 255:
                    letter_states = [1.0] * len(full_text)
                    typewriter_done = True
                    buttons_alpha = 255
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    selected = "YES"
                    vol = current_sfx_volume()
                    if menu_click_sound and vol > 0:
                        menu_click_sound.set_volume(vol)
                        menu_click_sound.play()
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    selected = "NO"
                    vol = current_sfx_volume()
                    if menu_click_sound and vol > 0:
                        menu_click_sound.set_volume(vol)
                        menu_click_sound.play()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button and yes_button.collidepoint(event.pos):
                    vol = current_sfx_volume()
                    if menu_click_sound and vol > 0:
                        menu_click_sound.set_volume(vol)
                        menu_click_sound.play()
                    pygame.display.flip()
                    pygame.time.wait(1000)
                    return True, initials
                elif no_button and no_button.collidepoint(event.pos):
                    vol = current_sfx_volume()
                    if menu_click_sound and vol > 0:
                        menu_click_sound.set_volume(vol)
                        menu_click_sound.play()
                    pygame.display.flip()
                    pygame.time.wait(1000)
                    return False, initials

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    return False, initials

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    print("Win Screen...")
    win_result = end_screen(screen, True)
    print(f"Win Screen Result: {'Restart' if win_result else 'Quit'}")

    pygame.time.wait(1000)

    print("Lose Screen...")
    lose_result = end_screen(screen, False)
    print(f"Lose Screen Result: {'Restart' if lose_result else 'Quit'}")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
