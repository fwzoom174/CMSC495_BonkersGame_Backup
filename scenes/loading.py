"""
This file draws the loading screen for the game.
It shows a pixel-style progress bar, loading text, and percent numbers.
"""

import pygame
import os
from common import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, ROOT_PATH


# Draw the loading screen while the game starts.
def show_loading_screen(screen, font):
    WHITE_COLOR = (255, 255, 255)  # White for all text and shapes

    BAR_WIDTH = 600  # Width of main bar
    BAR_HEIGHT = 60  # Height of main bar
    BAR_X = (SCREEN_WIDTH - BAR_WIDTH) // 2
    BAR_Y = SCREEN_HEIGHT // 2 + 60

    # Try to load pixel-style font
    pixel_font_path = os.path.join(
        ROOT_PATH,
        'media',
        'graphics',
        'font',
        'Pixeboy.ttf'
    )

    try:
        pixel_font_large = pygame.font.Font(pixel_font_path, 72)
        pixel_font_small = pygame.font.Font(pixel_font_path, 48)
    except:
        # Use default font if pixel font fails
        pixel_font_large = pygame.font.Font(None, 72)
        pixel_font_small = pygame.font.Font(None, 48)

    # Go from 0% to 100%
    for progress in range(101):
        screen.fill(BLACK)

        # ---------- LOADING TEXT ----------
        loading_text = pixel_font_large.render("LOADING...", True, WHITE_COLOR)
        loading_rect = loading_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        )
        screen.blit(loading_text, loading_rect)

        # ---------- PIXEL BORDER ----------
        border_thickness = 8
        pixel_size = 10  # pixel block size for border look

        # Top border
        for x in range(BAR_X, BAR_X + BAR_WIDTH, pixel_size):
            pygame.draw.rect(screen, WHITE_COLOR, (x, BAR_Y, pixel_size, border_thickness))

        # Bottom border
        for x in range(BAR_X, BAR_X + BAR_WIDTH, pixel_size):
            pygame.draw.rect(
                screen,
                WHITE_COLOR,
                (x, BAR_Y + BAR_HEIGHT - border_thickness, pixel_size, border_thickness)
            )

        # Left border
        for y in range(BAR_Y, BAR_Y + BAR_HEIGHT, pixel_size):
            pygame.draw.rect(screen, WHITE_COLOR, (BAR_X, y, border_thickness, pixel_size))

        # Right border
        for y in range(BAR_Y, BAR_Y + BAR_HEIGHT, pixel_size):
            pygame.draw.rect(
                screen,
                WHITE_COLOR,
                (BAR_X + BAR_WIDTH - border_thickness, y, border_thickness, pixel_size)
            )

        # ---------- PROGRESS BAR FILL ----------
        max_blocks = 20  # total blocks inside the bar
        blocks_to_show = int((progress / 100) * max_blocks)

        if blocks_to_show > 0:
            padding = 10  # space between border and blocks
            gap_size = 10  # space between each block

            # Calculate free width for blocks
            total_gap_space = gap_size * (max_blocks - 1)
            available_width = BAR_WIDTH - (border_thickness * 2) - (padding * 2) - total_gap_space

            block_width = available_width // max_blocks
            block_height = BAR_HEIGHT - (border_thickness * 2) - (padding * 2)

            # Draw each filled block
            for i in range(blocks_to_show):
                block_x = BAR_X + border_thickness + padding + (i * (block_width + gap_size))
                block_y = BAR_Y + border_thickness + padding
                pygame.draw.rect(screen, WHITE_COLOR, (block_x, block_y, block_width, block_height))

        # ---------- PERCENTAGE TEXT ----------
        percent_text = pixel_font_small.render(f"{progress}%", True, WHITE_COLOR)
        percent_rect = percent_text.get_rect(center=(SCREEN_WIDTH // 2, BAR_Y + BAR_HEIGHT + 40))
        screen.blit(percent_text, percent_rect)

        pygame.display.flip()
        pygame.time.wait(10)