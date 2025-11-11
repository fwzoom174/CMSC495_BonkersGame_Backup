import pygame
import os
import sys
from common import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW
from scenes.win_lose import draw_retro_background
from datetime import datetime, timezone, timedelta

# ---------- INITIALIZATION ----------
pygame.font.init()

# Initialize the mixer for sound
pygame.mixer.init()

# ---------- SOUND LOADING ----------
# Load sound effects

try:
    menu_click_sound = pygame.mixer.Sound(os.path.join("media", "audio", "media_audio_selection_click.wav"))
except:
    print("Warning: Could not load menu click sound.")
    menu_click_sound = None

# ---------- FONT UTILITIES ----------
def load_custom_font(size):
    font_path = os.path.join(os.path.dirname(__file__), "..", "media", "graphics", "font", "Pixeboy.ttf")
    return pygame.font.Font(font_path, size)


# ---------- SCORE MANAGEMENT ----------
def load_scores(file_path):
    scores = []
    if not os.path.exists(file_path):
        return scores
    with open(file_path, "r") as f:
        for line in f.readlines():
            parts = line.strip().split()
            if len(parts) == 3:
                initials, score, time = parts
                scores.append((initials.upper(), int(score), float(time)))
    scores.sort(key=lambda x: (-x[1], x[2]))
    return scores[:10]

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

def reset_today_scores_if_new_day(today_file):
    """Clear today's scores if the date has changed."""
    base_path = os.path.dirname(today_file)
    last_reset_path = os.path.join(base_path, "last_reset.txt")

    # Central Time offset
    central_offset = timedelta(hours=-5)
    now_cst = datetime.now(timezone(central_offset))
    today_date = now_cst.strftime("%Y-%m-%d")

    # Read last reset date
    last_date = None
    if os.path.exists(last_reset_path):
        with open(last_reset_path, "r") as f:
            last_date = f.read().strip()

    # If new day clear today file and update reset file
    if last_date != today_date:
        open(today_file, "w").close()  # clear file
        with open(last_reset_path, "w") as f:
            f.write(today_date)
            
# ---------- HIGH SCORES DISPLAY ----------
def show_high_scores(screen):
    running = True
    clock = pygame.time.Clock()

    title_font = load_custom_font(70)
    header_font = load_custom_font(40)
    text_font = load_custom_font(48)

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    today_file = os.path.join(base_path, "today_scores.txt")
    all_time_file = os.path.join(base_path, "records_alltime.txt")

    # Reset today's scores if the date has changed
    reset_today_scores_if_new_day(today_file)

    # Load both files (today + all-time)
    today_scores = load_scores(today_file)
    all_time_scores = load_scores(all_time_file)

    rank_colors = [(0, 255, 255), (255, 105, 180), (255, 255, 0), (255, 120, 60)]

    while running:
        draw_retro_background(screen)

        title_text = title_font.render("HIGH SCORES", True, YELLOW)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 60))

        today_title = header_font.render("TODAY'S HIGH SCORES", True, YELLOW)
        alltime_title = header_font.render("ALL-TIME HIGH SCORES", True, YELLOW)
        screen.blit(today_title, (SCREEN_WIDTH // 4 - today_title.get_width() // 2, 150))
        screen.blit(alltime_title, (3 * SCREEN_WIDTH // 4 - alltime_title.get_width() // 2, 150))

        y_start = 220
        spacing = 38

        # Column widths
        rank_w = text_font.size("10")[0]
        init_w = text_font.size("WWW")[0]
        score_w = text_font.size("999999")[0]
        time_w = text_font.size("00:00")[0]
        col_gap = 24

        def draw_table(x_base, scores):
            for i in range(10):
                color = rank_colors[i % len(rank_colors)]
                y = y_start + i * spacing

                if i < len(scores):
                    initials, score, t = scores[i]
                    surf = text_font.render(f"{i + 1}", True, color)
                    screen.blit(surf, (x_base, y))
                    surf = text_font.render(initials, True, color)
                    screen.blit(surf, (x_base + rank_w + col_gap, y))
                    surf = text_font.render(str(score), True, color)
                    screen.blit(surf, (x_base + rank_w + col_gap + init_w + col_gap +
                                       (score_w - surf.get_width()), y))
                    t_str = format_time(t)
                    surf = text_font.render(t_str, True, color)
                    screen.blit(surf, (x_base + rank_w + col_gap + init_w + col_gap +
                                       score_w + col_gap + (time_w - surf.get_width()), y))
                else:
                    empty_color = (150, 150, 150)
                    screen.blit(text_font.render(f"{i + 1}", True, empty_color), (x_base, y))
                    screen.blit(text_font.render("---", True, empty_color), (x_base + rank_w + col_gap, y))
                    screen.blit(text_font.render("----", True, empty_color),
                                (x_base + rank_w + col_gap + init_w + col_gap +
                                 score_w - text_font.size("----")[0], y))
                    screen.blit(text_font.render("--:--", True, empty_color),
                                (x_base + rank_w + col_gap + init_w + col_gap +
                                 score_w + col_gap + time_w - text_font.size("--:--")[0], y))

        # Left and right table anchors
        left_x = SCREEN_WIDTH // 4 - (rank_w + col_gap + init_w + col_gap + score_w + col_gap + time_w) // 2
        right_x = 3 * SCREEN_WIDTH // 4 - (rank_w + col_gap + init_w + col_gap + score_w + col_gap + time_w) // 2

        draw_table(left_x, today_scores)
        draw_table(right_x, all_time_scores)

        footer_text = text_font.render("PRESS ESC TO RETURN", True, (220, 20, 60))
        screen.blit(footer_text, (SCREEN_WIDTH // 2 - footer_text.get_width() // 2, SCREEN_HEIGHT - 175))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if menu_click_sound:
                        menu_click_sound.play()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if menu_click_sound:
                        menu_click_sound.play()
                running = False

        pygame.display.flip()
        clock.tick(60)