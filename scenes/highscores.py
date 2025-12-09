"""
This file draws the High Scores screen.
It loads the score files, sorts them,
and shows both today's scores and all-time scores.
"""

import pygame
import os
import sys
import json
from common import SCREEN_WIDTH, SCREEN_HEIGHT, YELLOW, ROOT_PATH
from scenes.win_lose import draw_retro_background
from datetime import datetime, timezone, timedelta

# ---------- INITIALIZATION ----------
pygame.font.init()

# Initialize the mixer for sound
if not pygame.mixer.get_init():
    pygame.mixer.init()

# ---------- SOUND LOADING ----------
# Load sound effects for menu actions
try:
    menu_click_sound = pygame.mixer.Sound(
        os.path.join(ROOT_PATH, "media", "audio", "media_audio_selection_click.wav")
    )
except:
    print("Warning: Could not load menu click sound.")
    menu_click_sound = None

config_path = "config.json"


# ---------- SOUND SETTINGS ----------
# Get current SFX volume as a value from 0.0 to 1.0
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


# ---------- FONT UTILITIES ----------
# Load the custom game font at the given size
def load_custom_font(size):
    font_path = os.path.join(ROOT_PATH, "media", "graphics", "font", "Pixeboy.ttf")
    return pygame.font.Font(font_path, size)


# ---------- SCORE MANAGEMENT ----------
# Load scores from a file and return the top 10 (sorted)
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


# Turn total seconds into "MM:SS" format
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"


# Clear today's scores if the calendar day has changed
def reset_today_scores_if_new_day(today_file):
    last_reset_path = "last_reset.txt"

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
# Show the high scores screen until the player presses ESC or closes the window
def show_high_scores(screen):
    running = True
    clock = pygame.time.Clock()

    title_font = load_custom_font(70)
    header_font = load_custom_font(40)
    text_font = load_custom_font(48)

    today_file = "today_scores.txt"
    all_time_file = "records_alltime.txt"

    # Reset today's scores if the date has changed
    reset_today_scores_if_new_day(today_file)

    # Load both files (today + all-time)
    today_scores = load_scores(today_file)
    all_time_scores = load_scores(all_time_file)

    rank_colors = [
        (0, 255, 255),
        (255, 105, 180),
        (255, 255, 0),
        (255, 120, 60),
    ]

    while running:
        draw_retro_background(screen)

        title_text = title_font.render("HIGH SCORES", True, YELLOW)
        screen.blit(
            title_text,
            (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 60)
        )

        today_title = header_font.render("TODAY'S HIGH SCORES", True, YELLOW)
        alltime_title = header_font.render("ALL-TIME HIGH SCORES", True, YELLOW)

        screen.blit(
            today_title,
            (SCREEN_WIDTH // 4 - today_title.get_width() // 2, 150)
        )
        screen.blit(
            alltime_title,
            (3 * SCREEN_WIDTH // 4 - alltime_title.get_width() // 2, 150)
        )

        y_start = 220
        spacing = 38

        # Column widths
        rank_w = text_font.size("10")[0]
        init_w = text_font.size("WWW")[0]
        score_w = text_font.size("999999")[0]
        time_w = text_font.size("00:00")[0]
        col_gap = 24

        # Draw one high-score column (table) at a given x position
        def draw_table(x_base, scores):
            for i in range(10):
                color = rank_colors[i % len(rank_colors)]
                y = y_start + i * spacing

                if i < len(scores):
                    initials, score, t = scores[i]

                    # Rank number
                    surf = text_font.render(f"{i + 1}", True, color)
                    screen.blit(surf, (x_base, y))

                    # Player initials
                    surf = text_font.render(initials, True, color)
                    screen.blit(surf, (x_base + rank_w + col_gap, y))

                    # Score value
                    surf = text_font.render(str(score), True, color)
                    screen.blit(
                        surf,
                        (
                            x_base + rank_w + col_gap + init_w + col_gap
                            + (score_w - surf.get_width()),
                            y
                        )
                    )

                    # Time string
                    t_str = format_time(t)
                    surf = text_font.render(t_str, True, color)
                    screen.blit(
                        surf,
                        (
                            x_base + rank_w + col_gap + init_w + col_gap
                            + score_w + col_gap + (time_w - surf.get_width()),
                            y
                        )
                    )
                else:
                    # Empty row placeholders
                    empty_color = (150, 150, 150)

                    screen.blit(
                        text_font.render(f"{i + 1}", True, empty_color),
                        (x_base, y)
                    )
                    screen.blit(
                        text_font.render("---", True, empty_color),
                        (x_base + rank_w + col_gap, y)
                    )
                    screen.blit(
                        text_font.render("----", True, empty_color),
                        (
                            x_base + rank_w + col_gap + init_w + col_gap
                            + score_w - text_font.size("----")[0],
                            y
                        )
                    )
                    screen.blit(
                        text_font.render("--:--", True, empty_color),
                        (
                            x_base + rank_w + col_gap + init_w + col_gap
                            + score_w + col_gap
                            + time_w - text_font.size("--:--")[0],
                            y
                        )
                    )

        # Left and right table anchors
        total_width = rank_w + col_gap + init_w + col_gap + score_w + col_gap + time_w
        left_x = SCREEN_WIDTH // 4 - total_width // 2
        right_x = 3 * SCREEN_WIDTH // 4 - total_width // 2

        draw_table(left_x, today_scores)
        draw_table(right_x, all_time_scores)

        footer_text = text_font.render("BACK (ESC)", True, (220, 20, 60))
        screen.blit(
            footer_text,
            (SCREEN_WIDTH // 2 - footer_text.get_width() // 2, SCREEN_HEIGHT - 175)
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if menu_click_sound and current_sfx_volume() > 0:
                    menu_click_sound.set_volume(current_sfx_volume())
                    menu_click_sound.play()
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if menu_click_sound and current_sfx_volume() > 0:
                    menu_click_sound.set_volume(current_sfx_volume())
                    menu_click_sound.play()
                running = False

        pygame.display.flip()
        clock.tick(60)