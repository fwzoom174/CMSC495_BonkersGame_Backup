import pygame
import os
import sys
from common import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, ORANGE
from scenes.win_lose import draw_retro_background

# Initialize pygame font
pygame.font.init()

# Load custom retro font
def load_custom_font(size):
    font_path = os.path.join(os.path.dirname(__file__), "..", "media", "graphics", "font", "Pixeboy.ttf")
    return pygame.font.Font(font_path, size)

# Read and sort score data from text file
def load_scores(file_path):
    scores = []
    if not os.path.exists(file_path):
        return scores
    with open(file_path, "r") as f:
        for line in f.readlines():
            parts = line.strip().split()
            if len(parts) == 3:  # format: initials, score, time
                initials, score, time = parts
                scores.append((initials.upper(), int(score), float(time)))
    # Sort by score descending, then by fastest time
    scores.sort(key=lambda x: (-x[1], x[2]))
    return scores[:10]  # only keep top 10

# Format seconds into MM:SS display
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

def show_high_scores(screen):
    """Show today's and all-time high scores with retro background and layout."""
    running = True
    clock = pygame.time.Clock()

    # Set up fonts
    title_font = load_custom_font(70)
    header_font = load_custom_font(40)
    text_font = load_custom_font(32)

    # Paths for score files
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    today_file = os.path.join(base_path, "today_scores.txt")
    all_time_file = os.path.join(base_path, "records_alltime.txt")

    # Load both files (today + all-time)
    today_scores = load_scores(today_file)
    all_time_scores = load_scores(all_time_file)

    while running:
        # Draw retro background grid
        draw_retro_background(screen)

        # Main title
        title_text = title_font.render("HIGH SCORES", True, YELLOW)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 60))

        # Section headers
        today_title = header_font.render("TODAY'S HIGH SCORES", True, WHITE)
        alltime_title = header_font.render("ALL-TIME HIGH SCORES", True, WHITE)

        screen.blit(today_title, (SCREEN_WIDTH // 4 - today_title.get_width() // 2, 150))
        screen.blit(alltime_title, (3 * SCREEN_WIDTH // 4 - alltime_title.get_width() // 2, 150))

        # Set list spacing
        y_start = 220
        spacing = 38

        # Loop through both lists and draw side-by-side
        for i in range(10):
            # LEFT SIDE (today's top scores)
            if i < len(today_scores):
                initials, score, time_val = today_scores[i]
                entry = f"{i+1}. {initials:<3}  {score:<5}  {format_time(time_val)}"
                text = text_font.render(entry, True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 4 - 150, y_start + i * spacing))
            else:
                empty_text = text_font.render(f"{i+1}. ---   ----   --:--", True, (150, 150, 150))
                screen.blit(empty_text, (SCREEN_WIDTH // 4 - 150, y_start + i * spacing))

            # RIGHT SIDE (all-time top scores)
            if i < len(all_time_scores):
                initials, score, time_val = all_time_scores[i]
                entry = f"{i+1}. {initials:<3}  {score:<5}  {format_time(time_val)}"
                text = text_font.render(entry, True, WHITE)
                screen.blit(text, (3 * SCREEN_WIDTH // 4 - 150, y_start + i * spacing))
            else:
                empty_text = text_font.render(f"{i+1}. ---   ----   --:--", True, (150, 150, 150))
                screen.blit(empty_text, (3 * SCREEN_WIDTH // 4 - 150, y_start + i * spacing))

        # Footer for exiting the screen
        footer_text = text_font.render("Press ESC to return", True, ORANGE)
        screen.blit(footer_text, (SCREEN_WIDTH // 2 - footer_text.get_width() // 2, SCREEN_HEIGHT - 80))

        # Handle ESC key or quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        pygame.display.flip()
        clock.tick(60)
