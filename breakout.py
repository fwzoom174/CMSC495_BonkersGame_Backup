import sys
import pygame
from pygame import Rect

screen_width, screen_height = 800, 600

# Set up colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)

def draw_gradient_background(screen, top_color, bottom_color):
    """Draw a simple vertical gradient for the menu background"""
    for y in range(screen_height):
        ratio = y / screen_height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (screen_width, y))

def main_menu():
    # Set up the screen
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Breakout Game - Menu")
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)

    # Set up the title and buttons
    title = font.render("Breakout Game", True, WHITE)
    play_button = small_font.render("Play", True, BLUE)
    quit_button = small_font.render("Quit", True, RED)
    how_button = small_font.render("How to Play", True, GREEN)

    play_rect = play_button.get_rect(center=(screen_width // 2, 320))
    how_rect = how_button.get_rect(center=(screen_width // 2, 400))
    quit_rect = quit_button.get_rect(center=(screen_width // 2, 480))

    running = True
    while running:
        # Fill the screen with a gradient background
        draw_gradient_background(screen, (20, 20, 60), (0, 0, 0))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 150))

        # Draw menu buttons
        for button, rect in [(play_button, play_rect), (how_button, how_rect), (quit_button, quit_rect)]:
            screen.blit(button, rect)

        # Detect mouse hover over buttons
        mouse_pos = pygame.mouse.get_pos()
        for rect in [play_rect, how_rect, quit_rect]:
            if rect.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                break
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    running = False
                elif how_rect.collidepoint(event.pos):
                    show_instructions(screen)
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False

        # Update the display
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def show_instructions(screen):
    """Simple instruction screen"""
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)

    # Display the list of controls and instructions
    instructions = [
        "Use the arrow keys or A/D to move the paddle.",
        "Bounce the ball to break all the blocks.",
        "You have 3 lives. The game ends when they run out.",
        "Press ESC to go back to the menu."
    ]

    waiting = True
    while waiting:
        # Fill background with gradient for consistency
        draw_gradient_background(screen, (10, 10, 50), (0, 0, 0))

        # Draw the "How to Play" title
        title = font.render("How to Play", True, WHITE)
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 120))

        # Draw each instruction line
        y = 220
        for line in instructions:
            text = small_font.render(line, True, WHITE)
            screen.blit(text, (screen_width // 2 - text.get_width() // 2, y))
            y += 50

        # Return message
        back_text = small_font.render("Press ESC to return", True, RED)
        screen.blit(back_text, (screen_width // 2 - back_text.get_width() // 2, y + 40))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)

def main_controller():
    level = 0

    # Set up the screen
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Breakout Game")

    # Set up lives and font
    lives = 3
    font = pygame.font.Font(None, 36)

    # Set up the initial position and speed of the paddle
    bar_height = 20
    bar_width = 200
    bar_x = (screen_width - bar_width) // 2
    bar_y = screen_height - bar_height - 50
    speed = 5

    # Set up the initial position and speed of the ball
    ball_x = screen_width // 2
    ball_y = screen_height // 2
    ball_radius = 10
    ball_speed_x = 5
    ball_speed_y = 5
    ball_direction_x = 0
    ball_direction_y = 1

    # Generate the block layout
    blocks = define_blocks(level)

    running = True
    while running:
        # Constrain the ball to the screen bounds
        if ball_x + ball_radius >= screen_width or ball_x - ball_radius <= 0:
            ball_direction_x *= -1
        if ball_y - ball_radius <= 0:
            ball_direction_y *= -1

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Key presses handling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if bar_x + bar_width < screen_width:
                bar_x += speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if bar_x > 0:
                bar_x -= speed

        # Fill the screen with black color
        screen.fill(BLACK)

        # Draw the paddle
        bar = pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))

        # Save previous ball position and move the ball
        prev_x, prev_y = ball_x, ball_y
        ball_x += int(ball_speed_x * ball_direction_x)
        ball_y += int(ball_speed_y * ball_direction_y)

        # Draw the ball
        ball = pygame.draw.circle(screen, WHITE, (ball_x, ball_y), ball_radius)

        # Is the ball touching the paddle
        if bar.colliderect(ball):
            if bar.centerx > ball.centerx + 10:
                ball_direction_x = -0.5
            elif bar.centerx < ball.centerx - 10:
                ball_direction_x = 0.5
            else:
                ball_direction_x = 0
            ball_direction_y *= -1
            # Nudge the ball above the paddle to avoid sticking
            ball_y = bar.top - ball_radius - 1

        # Draw the blocks and check for collisions
        for block in blocks[:]:
            pygame.draw.rect(screen, block.color, block.rect)
            if block.rect.colliderect(ball):
                hit_vertical = prev_y <= block.rect.top or prev_y >= block.rect.bottom
                if hit_vertical:
                    ball_direction_y *= -1
                    if prev_y <= block.rect.top:
                        ball_y = block.rect.top - ball_radius - 1
                    else:
                        ball_y = block.rect.bottom + ball_radius + 1
                else:
                    ball_direction_x *= -1
                    if prev_x <= block.rect.left:
                        ball_x = block.rect.left - ball_radius - 1
                    else:
                        ball_x = block.rect.right + ball_radius + 1
                blocks.remove(block)

        # Check if the ball goes below the paddle
        if ball_y - ball_radius > screen_height:
            lives -= 1
            if lives > 0:
                # Reset ball and paddle
                ball_x = screen_width // 2
                ball_y = screen_height // 2
                bar_x = (screen_width - bar_width) // 2
                ball_direction_x = 0
                ball_direction_y = 1

                # Show "Life lost" message and wait 3 seconds
                message = font.render(f"Lives left: {lives}", True, WHITE)
                screen.blit(message, (screen_width // 2 - message.get_width() // 2, screen_height // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
            else:
                # Out of lives, end game
                running = False

        # End the game if all blocks are cleared
        if len(blocks) == 0:
            running = False

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        pygame.time.Clock().tick(60)

    # Quit Pygame
    pygame.quit()
    sys.exit()

class Block:
    def __init__(self, rect, color):
        self.rect = rect
        self.color = color

def define_blocks(level):
    blocks = []
    num_blocks = 1
    block_width = 60
    block_height = 25
    block_space = 10
    row = 0

    # Set up colors for each row
    color_list = [RED, (255, 165, 0), YELLOW, GREEN, BLUE, PURPLE, CYAN]

    if level == 0:
        num_blocks = 66

    column = 0

    # Calculate how many blocks fit per row
    blocks_per_row = (screen_width - block_space) // (block_width + block_space)

    for i in range(num_blocks):
        # Calculate block's X position
        block_x = column * (block_width + block_space)

        # Does the block pass the screen edge? If so, move to next row
        if column >= blocks_per_row:
            row += 1
            column = 0
            block_x = column * (block_width + block_space)

        # Add the block to the list and increment the column
        color = color_list[row % len(color_list)]
        blocks.append(Block(Rect(block_x + block_space, (block_height * row) + (block_space * row) + 50,
                                 block_width, block_height), color))
        column += 1

    return blocks

if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    # Start the main menu and game
    main_menu()
    main_controller()
