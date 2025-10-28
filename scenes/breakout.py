import sys
import pygame
import common

from common import BLACK, WHITE, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, CYAN
from objects.block import Block
from objects.scoreboard import ScoreBoard

clock = pygame.time.Clock()
delta_time = 1

def main_controller(screen):
    global delta_time
    level = 0

    screen_width, screen_height = screen.get_size()

    # Set up the screen
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Breakout Game")
    # Initialize the scoreboard for tracking score, lives, and high score
    scoreboard = ScoreBoard(screen)

    font = pygame.font.Font(None, 36)

    # Set up the initial position and speed of the paddle
    bar_height = 20
    bar_width = 200
    bar_x = (screen_width - bar_width) // 2
    bar_y = screen_height - bar_height - 50
    speed = 5

    # Set up the initial position and velocity of the ball
    ball_radius = 10
    ball_position = pygame.Vector2(screen_width // 2, screen_height // 2)
    ball_velocity = pygame.Vector2(0, 5)
    ball_max_velocity_x = 5

    # Generate the block layout
    blocks = define_blocks(screen, level)

    running = True
    while running:
        # Constrain the ball to the screen bounds
        if ball_position.x + ball_radius >= screen_width or ball_position.x - ball_radius <= 0:
            ball_velocity.x *= -1
        if ball_position.y - ball_radius <= 0:
            ball_velocity.y *= -1

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
        prev_x, prev_y = ball_position.x, ball_position.y
        ball_position.move_towards_ip(ball_position + ball_velocity, 10)
        ball = pygame.draw.circle(screen, WHITE, ball_position, ball_radius)

        # Is the ball touching the paddle
        if bar.colliderect(ball):
            # Calculate where on the paddle the ball collided. Invert it so positive offset is right and negative is left
            ball_offset = (bar.centerx - ball.centerx) * -1
            # Using the max x velocity, determine how much weight to apply to the offset to set an appropriate x speed
            ratio = ball_max_velocity_x / (bar_width / 2)
            # Set the x velocity based on the offset and ratio
            ball_velocity.x = ball_offset * ratio
            # Send the ball back up
            ball_velocity.y *= -1
            # Nudge the ball above the paddle to avoid sticking
            ball_position.y = bar.top - ball_radius - 1

        # Draw the blocks and check for collisions
        for block in blocks[:]:
            pygame.draw.rect(screen, block.color, block.rect)
            if block.rect.colliderect(ball):
                hit_vertical = prev_y <= block.rect.top or prev_y >= block.rect.bottom
                if hit_vertical:
                    ball_velocity.y *= -1
                    if prev_y <= block.rect.top:
                        ball_position.y = block.rect.top - ball_radius - 1
                    else:
                        ball_position.y = block.rect.bottom + ball_radius + 1
                else:
                    ball_velocity.x *= -1
                    if prev_x <= block.rect.left:
                        ball_position.x = block.rect.left - ball_radius - 1
                    else:
                        ball_position.x = block.rect.right + ball_radius + 1
                blocks.remove(block)
                # Add points when a block is destroyed
                scoreboard.add_points(50)

        # Check if the ball goes below the paddle
        if ball_position.y - ball_radius > screen_height:
            scoreboard.lose_life()
            if scoreboard.lives > 0:
                # Reset ball and paddle
                ball_position.x = screen_width // 2
                ball_position.y = screen_height // 2
                bar_x = (screen_width - bar_width) // 2
                ball_velocity.x = 0
                ball_velocity.y = 5

                # Show "Life lost" message and wait 3 seconds
                message = font.render(f"Lives Left: {scoreboard.lives}", True, WHITE)
                screen.blit(message, (screen_width // 2 - message.get_width() // 2, screen_height // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
            else:
                scoreboard.save_high_score()
                # Out of lives, end game
                running = False

        # End the game if all blocks are cleared
        if len(blocks) == 0:
            running = False

        # Draw scoreboard elements (score, lives, and high score)
        scoreboard.draw()

        # Update the display
        pygame.display.flip()

        # Useful in performing motion over time calculations - e.g. falling power ups?
        delta_time = clock.tick(60)

    # Save high score at the end of the game
    scoreboard.save_high_score()

    # Quit Pygame
    pygame.quit()
    sys.exit()

def define_blocks(screen, level):
    blocks = []
    num_blocks = 1
    block_width = 60
    block_height = 25
    block_space = 10
    row = 0

    # Set up colors for each row
    color_list = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, CYAN]

    if level == 0:
        num_blocks = 68

    column = 0

    # Calculate how many blocks fit per row
    blocks_per_row = (screen.get_width() - block_space) // (block_width + block_space)

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
        blocks.append(Block(pygame.Rect(block_x + block_space, (block_height * row) + (block_space * row) + 50,
                                        block_width, block_height), color))
        column += 1

    return blocks

def play(screen):
    main_controller(screen)


if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    play(pygame.display.set_mode((common.screen_width, common.screen_height)))
