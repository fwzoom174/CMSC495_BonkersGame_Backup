import pygame
import common

from common import BLACK, WHITE, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, CYAN, SCREEN_WIDTH, SCREEN_HEIGHT
from objects.block import Block
from objects.scoreboard import ScoreBoard
from scenes.win_lose import end_screen
from objects.timer import Timer  # Added import for new timer feature
from scenes.pause_overlay import pause_overlay

# Paddle constants
BAR_WIDTH = 200
BAR_HEIGHT = 20

clock = pygame.time.Clock()
delta_time = 1

# Load background image
try:
    background = pygame.image.load("media/graphics/background/back-black.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    print("Warning: Could not load background image. Using black background.")
    background = None

# Initialize the mixer for sound
pygame.mixer.init()

# Load sound effects
try:
    wall_sound = pygame.mixer.Sound("media/audio/media_audio_wall-hit.wav")
    paddle_sound = pygame.mixer.Sound("media/audio/media_audio_paddle-hit.wav")
    brick_sound = pygame.mixer.Sound("media/audio/media_audio_brick-hit.ogg")
except:
    print("Warning: Could not load sound files. Game will run without sound.")
    wall_sound = None
    paddle_sound = None
    brick_sound = None

# Load paddle image
try:
    paddle_image = pygame.image.load("media/graphics/paddle/paddle.png")
    paddle_image = pygame.transform.scale(paddle_image, (BAR_WIDTH, BAR_HEIGHT))
except:
    paddle_image = None
    print("Warning: Could not load paddle image")

def main_controller(screen, debug_mode=False):
    global delta_time
    level = 1
    win = False

    # Set up the screen
    pygame.display.set_caption("Breakout Game")
    # Initialize the scoreboard for tracking score, lives, and high score
    scoreboard = ScoreBoard(screen)
    if debug_mode:
        level = 0
        scoreboard.lives = 1

    # Added timer setup (stopwatch for normal, countdown for challenge mode)
    timer = Timer(screen, mode="stopwatch")  # default
    if debug_mode == "countdown":
        timer = Timer(screen, mode="countdown", countdown_time=10)

    font = pygame.font.Font(None, 36)


    # Load pixel font for messages
    import os
    pixel_font_path = os.path.join(os.path.dirname(__file__), '..', 'media', 'graphics', 'font', 'Pixeboy.ttf')
    pixel_font = pygame.font.Font(pixel_font_path, 36)

    # Set up the initial position and speed of the paddle
    bar_height = BAR_HEIGHT
    bar_width = BAR_WIDTH
    bar_x = (SCREEN_WIDTH - bar_width) // 2
    bar_y = SCREEN_HEIGHT - bar_height - 100
    speed = 5

    # Set up the initial position and velocity of the ball
    ball_radius = 10
    ball_position = pygame.Vector2(SCREEN_WIDTH // 2, bar_y - ball_radius - 1)
    prev_x, prev_y = ball_position.x, ball_position.y
    ball_velocity = pygame.Vector2(0, 0)
    ball_max_velocity_x = 5

    # Generate the block layout
    blocks, brick_images = define_blocks(screen, level)
    for block in blocks:
        # Try to draw brick image, fallback to rectangle
        if block.color in brick_images and brick_images[block.color]:
            screen.blit(brick_images[block.color], block.rect)
        else:
            pygame.draw.rect(screen, block.color, block.rect)

    running = True
    while running:
        # Fill the screen with black color
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)

        # Draw the paddle
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        if paddle_image:
            screen.blit(paddle_image, (bar_x, bar_y))
        else:
            pygame.draw.rect(screen, RED, bar_rect)
        bar = bar_rect
        
        ball = pygame.draw.circle(screen, WHITE, ball_position, ball_radius)
        # Constrain the ball to the screen bounds
        if ball_position.x + ball_radius >= SCREEN_WIDTH or ball_position.x - ball_radius <= 0:
            ball_velocity.x *= -1
            # PLAY WALL SOUND
            if wall_sound:
                wall_sound.play()

        if ball_position.y - ball_radius <= 0:
            ball_velocity.y *= -1
            # PLAY WALL SOUND
            if wall_sound:
                wall_sound.play()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Launch ball on first space press
                if event.key == pygame.K_SPACE and ball_velocity.y == 0:
                    ball_velocity.x = get_x_velocity(bar, ball, ball_max_velocity_x, bar_width)
                    ball_velocity.y = -5
                    timer.resume()
                # Request pause
                if event.key == pygame.K_ESCAPE:
                    pause_requested = True

        # Key presses handling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if bar_x + bar_width < SCREEN_WIDTH and not (bar_x > ball_position.x - ball_radius and ball_velocity.y == 0):
                bar_x += speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if bar_x > 0 and not (bar_x + bar_width < ball_position.x + ball_radius and ball_velocity.y == 0):
                bar_x -= speed

        if ball_velocity.y == 0:
            msg = pixel_font.render("PRESS [SPACE] TO BEGIN", True, (255, 255, 0))
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2))
        else:
            # Save previous ball position and move the ball
            prev_x, prev_y = ball_position.x, ball_position.y
            ball_position.move_towards_ip(ball_position + ball_velocity, 10)

            # Is the ball touching the paddle
            if bar.colliderect(ball):
                ball_velocity.x = get_x_velocity(bar, ball, ball_max_velocity_x, bar_width)
                # Send the ball back up
                ball_velocity.y *= -1
                # Nudge the ball above the paddle to avoid sticking
                ball_position.y = bar.top - ball_radius - 1
                # PLAY PADDLE SOUND
                if paddle_sound:
                    paddle_sound.play()

        # Draw the blocks and check for collisions
        for block in blocks:
            # Try to draw brick image, fallback to rectangle
            if block.color in brick_images and brick_images[block.color]:
                screen.blit(brick_images[block.color], block.rect)
            else:
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

                # Remove the block from the list of blocks
                blocks.remove(block)
                # Remove any remaining references to the hit block to make sure Python's garbage collection deletes it
                del block

                # Add points when a block is destroyed
                scoreboard.add_points(50)
                # PLAY BRICK SOUND
                if brick_sound:
                    brick_sound.play()

        # Check if the ball goes below the paddle
        if ball_position.y - ball_radius > SCREEN_HEIGHT:
            scoreboard.lose_life()
            timer.pause()  # pause timer when a life is lost
            if scoreboard.lives > 0:
                # Reset ball and paddle
                ball_position = pygame.Vector2(SCREEN_WIDTH // 2, bar_y - ball_radius - 1)
                bar_x = (SCREEN_WIDTH - bar_width) // 2
                ball_velocity.x = 0
                ball_velocity.y = 0

                # Show "Life lost" message and wait 3 seconds
                message = font.render(f"Lives Left: {scoreboard.lives}", True, WHITE)
                screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
            else:
                timer.pause()  # stop timer on final life loss
                # Out of lives, end game
                running = False

        # End the game if all blocks are cleared
        if len(blocks) == 0:
            timer.pause()  # pause timer when level is cleared
            running = False
            win = True

        # Draw scoreboard elements (score, lives, and high score)
        scoreboard.draw()

        # Added timer update and draw calls (shows elapsed or countdown)
        timer.update()
        timer.draw()

        # Check if countdown time has run out (for countdown mode)
        if debug_mode == "countdown" and timer.get_time() <= 0:
            scoreboard.lives = 0
            running = False

        # Pause handling
        if 'pause_requested' in locals() and pause_requested:
            snapshot = screen.copy()
            choice = pause_overlay(snapshot)
            if choice == "menu":
                return False
            pygame.event.clear()
            pause_requested = False

        # Update the display
        pygame.display.flip()

        # Useful in performing motion over time calculations - e.g. falling power ups?
        delta_time = clock.tick(60)

    # Added initials handling from win_lose screen + high score save with time
    replay, initials = end_screen(screen, win, scoreboard.score)
    scoreboard.save_high_score(initials=initials, current_time=timer.get_time())
    return replay


def get_x_velocity(bar, ball, ball_max_velocity_x, bar_width):
    # Calculate where on the paddle the ball collided. Invert it so positive offset is right and negative is left
    ball_offset = (bar.centerx - ball.centerx) * -1
    # Using the max x velocity, determine how much weight to apply to the offset to set an appropriate x speed
    ratio = ball_max_velocity_x / (bar_width / 2)
    # Set the x velocity based on the offset and ratio
    return ball_offset * ratio


def define_blocks(screen, level):
    blocks = []
    num_blocks = 68
    block_width = 60
    block_height = 25
    block_space = 10
    row = 0

    # Set up colors for each row
    color_list = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, CYAN]

    if level == 0:
        num_blocks = 1

    column = 0

     # Load brick images
    brick_images = {}
    color_names = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'cyan']
    
    for i, color_name in enumerate(color_names):
        try:
            img = pygame.image.load(f"media/graphics/bricks/{color_name}-brick.png")
            brick_images[color_list[i]] = pygame.transform.scale(img, (block_width, block_height))
        except:
            brick_images[color_list[i]] = None
            print(f"Warning: Could not load {color_name}-brick.png")

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
        blocks.append(Block(pygame.Rect(block_x + block_space, (block_height * row) + (block_space * row) + 150 ,
                                        block_width, block_height), color))
        column += 1

    return blocks, brick_images



def play(screen, debug_mode=False):
    return main_controller(screen, debug_mode)


if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    main_controller(pygame.display.set_mode((common.SCREEN_WIDTH, common.SCREEN_HEIGHT)))
