import pygame
import os
from common import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, ROOT_PATH

def show_loading_screen(screen, font):
    """Display loading screen with progress bar - PIXELATED RETRO STYLE"""
    WHITE_COLOR = (255, 255, 255)  # White for everything
    BAR_WIDTH = 600
    BAR_HEIGHT = 60
    BAR_X = (SCREEN_WIDTH - BAR_WIDTH) // 2
    BAR_Y = SCREEN_HEIGHT // 2 + 60
    
    # Try to load pixel font
    pixel_font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
    try:
        pixel_font_large = pygame.font.Font(pixel_font_path, 72)
        pixel_font_small = pygame.font.Font(pixel_font_path, 48)
    except:
        # Fallback to default font if pixel font not found
        pixel_font_large = pygame.font.Font(None, 72)
        pixel_font_small = pygame.font.Font(None, 48)
    
    # Simulate loading with progress bar
    for progress in range(101):
        screen.fill(BLACK)
        
        # Draw "LOADING..." text with pixelated font in white
        loading_text = pixel_font_large.render("LOADING...", True, WHITE_COLOR)
        text_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(loading_text, text_rect)
        
        # Draw pixelated progress bar border in white (made of pixel blocks)
        border_thickness = 8
        pixel_size = 10  
        
        # Draw top border (pixelated)
        for x in range(BAR_X, BAR_X + BAR_WIDTH, pixel_size):
            pygame.draw.rect(screen, WHITE_COLOR, (x, BAR_Y, pixel_size, border_thickness))
        
        # Draw bottom border (pixelated)
        for x in range(BAR_X, BAR_X + BAR_WIDTH, pixel_size):
            pygame.draw.rect(screen, WHITE_COLOR, (x, BAR_Y + BAR_HEIGHT - border_thickness, pixel_size, border_thickness))
        
        # Draw left border (pixelated)
        for y in range(BAR_Y, BAR_Y + BAR_HEIGHT, pixel_size):
            pygame.draw.rect(screen, WHITE_COLOR, (BAR_X, y, border_thickness, pixel_size))
        
        # Draw right border (pixelated)
        for y in range(BAR_Y, BAR_Y + BAR_HEIGHT, pixel_size):
            pygame.draw.rect(screen, WHITE_COLOR, (BAR_X + BAR_WIDTH - border_thickness, y, border_thickness, pixel_size))
        
        # Draw progress bar fill with exactly 10 vertical blocks (like the image)
        max_blocks = 20
        blocks_to_show = int((progress / 100) * max_blocks)
        
        if blocks_to_show > 0:
            # Add padding between border and blocks
            padding = 10  
            
            # Calculate block sizing to fit exactly 10 vertical blocks
            gap_size = 10  # Gap between blocks
            total_gap_space = gap_size * (max_blocks - 1)
            available_width = BAR_WIDTH - (border_thickness * 2) - (padding * 2) - total_gap_space
            block_width = available_width // max_blocks
            block_height = BAR_HEIGHT - (border_thickness * 2) - (padding * 2)
            
            for i in range(blocks_to_show):
                block_x = BAR_X + border_thickness + padding + (i * (block_width + gap_size))
                block_y = BAR_Y + border_thickness + padding
                
                # Use white color for blocks
                color = WHITE_COLOR
                
                # Draw the vertical block
                pygame.draw.rect(screen, color, (block_x, block_y, block_width, block_height))
        
        # Draw percentage text with pixelated font in white
        percent_text = pixel_font_small.render(f"{progress}%", True, WHITE_COLOR)
        percent_rect = percent_text.get_rect(center=(SCREEN_WIDTH // 2, BAR_Y + BAR_HEIGHT + 40))
        screen.blit(percent_text, percent_rect)
        
        pygame.display.flip()
        pygame.time.wait(10)  
