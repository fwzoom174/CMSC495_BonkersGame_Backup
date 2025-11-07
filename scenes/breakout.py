import pygame
import common
import os

from common import BLACK, WHITE, RED, COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, ROOT_PATH
from objects.block import Block
from objects.scoreboard import ScoreBoard
from scenes.win_lose import end_screen
from objects.timer import Timer  # Added import for new timer feature
from scenes.pause_overlay import pause_overlay

# WALL / BORDER 
WALL_PADDING = 30          
WALL_TOP_PADDING = 120     
WALL_THICKNESS = 10         
BRICKS_TOP = 140

# Fonts
pixel_font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
font = pygame.font.Font(pixel_font_path, 36)

# Set up the initial position and speed of the paddle
BAR_WIDTH = 200
BAR_HEIGHT = 20
bar_x = (SCREEN_WIDTH - BAR_WIDTH) // 2
bar_y = SCREEN_HEIGHT - BAR_HEIGHT - 100
speed = 5

# Set up the initial position and velocity of the ball
ball_radius = 10
ball_position = pygame.Vector2(SCREEN_WIDTH // 2, bar_y - ball_radius - 1)
ball_velocity = pygame.Vector2(0, 0)
ball_max_velocity_x = 5

clock = pygame.time.Clock()
delta_time = 1
pause_requested = False
win = False

# Load background image
try:
    background = pygame.image.load(os.path.join(ROOT_PATH, 'media', 'graphics', 'background', 'back-black-wall-border.png'))
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except FileNotFoundError:
    print("Warning: Could not load background image. Using black background.")
    background = None

# Initialize the mixer for sound
pygame.mixer.init()

# Load sound effects
try:
    wall_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_wall-hit.wav'))
    paddle_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_paddle-hit.wav'))
    brick_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_brick-hit.ogg'))
    lose_life_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_lose-lives.wav'))
except FileNotFoundError:
    print("Warning: Could not load sound files. Game will run without sound.")
    wall_sound = None
    paddle_sound = None
    brick_sound = None
    lose_life_sound = None

# Load paddle image
try:
    paddle_image = pygame.image.load(os.path.join(ROOT_PATH, 'media', 'graphics', 'paddle', 'paddle.png'))
    paddle_image = pygame.transform.scale(paddle_image, (BAR_WIDTH, BAR_HEIGHT))
except FileNotFoundError:
    paddle_image = None
    print("Warning: Could not load paddle image")

# This controls the initial setup of the breakout game and calls the game loop function
def main_controller(screen, debug_mode=False):
    level = 1

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

    # Generate the block layout
    blocks = define_blocks(screen, level)
    draw_bricks(screen, blocks)

    running = True
    while running:
        running = game_loop(screen, scoreboard, timer, blocks)

    # Added initials handling from win_lose screen + high score save with time
    replay, initials = end_screen(screen, win, scoreboard.score)
    scoreboard.save_high_score(initials=initials, current_time=timer.get_time())
    return replay

def define_blocks(screen, level, wall_padding=WALL_PADDING):
    blocks = []
    num_blocks = 64
    block_width, block_height = 60, 25
    block_space = 10
    row = column = 0

    # Debug mode
    if level == 0:
        num_blocks = 1

    # Calculate how many blocks fit per row inside the wall
    usable_width = screen.get_width() - (wall_padding * 2)
    blocks_per_row = (usable_width + block_space) // (block_width + block_space)

    # Calculate the total width of all blocks in a row
    total_blocks_width = blocks_per_row * block_width + (blocks_per_row - 1) * block_space
    # Calculate left offset to center the blocks
    left_offset = (screen.get_width() - total_blocks_width) // 2

    for i in range(num_blocks):
        # Move to next row when needed (check BEFORE calculating position)
        if column >= blocks_per_row:
            row += 1
            column = 0

        # Calculate block's X position - ALL blocks use the same left_offset
        block_x = left_offset + column * (block_width + block_space)

        # Y position also offset by BRICKS_TOP
        block_y = BRICKS_TOP + (block_height * row) + (block_space * row)

        color = COLORS[row % len(COLORS)]
        blocks.append(Block(pygame.Rect(block_x, block_y, block_width, block_height), color))
        column += 1

    return blocks

def game_loop(screen, scoreboard, timer, blocks, debug_mode=False):
    global ball_position, pause_requested, delta_time

    # Draw walls, paddle, ball, scoreboard, and timer
    walls = draw_wall(screen)
    bar = draw_bar(screen)
    ball = pygame.draw.circle(screen, WHITE, ball_position, ball_radius)
    scoreboard.draw()
    timer.draw()

    # Event handling
    if not handle_input(bar, ball, timer):
        return False

    # Draw the blocks and check for collisions
    draw_bricks(screen, blocks)
    scoreboard.score += detect_collision(ball, blocks)

    # End the game if all blocks are cleared
    if len(blocks) == 0:
        timer.pause()  # pause timer when level is cleared
        set_win()
        return False

    # Move the ball - False when the ball hits the bottom of the screen
    if not move_ball(screen, walls, bar, ball, scoreboard, timer):
        # Pause game, update lives, returns False when out of lives
        if not update_scoreboard(screen, scoreboard, timer):
            return False

    # Check if countdown time has run out (for countdown mode)
    if debug_mode == "countdown" and timer.get_time() <= 0:
        # scoreboard.lives = 0
        return False

    # Pause handling
    if pause_requested:
        if not pause_game(screen):
            # Player pressed quit on pause menu
            return False

    # Update the timer and display
    timer.update()
    pygame.display.flip()

    # Update delta_time tick(Frames per Second)
    delta_time = clock.tick(60)
    return True

def draw_wall(screen):
    # Fill the screen with black color
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BLACK)
    # Create the inner wall rectangle (inside screen edges)
    wall_bottom = SCREEN_HEIGHT - 150

    return pygame.Rect(
        WALL_PADDING,
        WALL_TOP_PADDING,
        SCREEN_WIDTH - WALL_PADDING * 2,
        wall_bottom - WALL_TOP_PADDING  # height from top wall to wall_bottom
    )

def draw_bar(screen):
    bar = pygame.Rect(bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT)
    if paddle_image:
        screen.blit(paddle_image, (bar_x, bar_y))
    else:
        pygame.draw.rect(screen, RED, bar)
    return bar

def handle_input(bar, ball, timer):
    global pause_requested, bar_x
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            # Launch ball on first space press
            if event.key == pygame.K_SPACE and ball_velocity.y == 0:
                ball_velocity.x = get_x_angle(bar, ball)
                ball_velocity.y = -5
                timer.resume()
            # Request pause
            if event.key == pygame.K_ESCAPE:
                pause_requested = True

    # Key presses handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        if bar_x + BAR_WIDTH < SCREEN_WIDTH and not (bar_x > ball_position.x - ball_radius and ball_velocity.y == 0):
            bar_x += speed
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        if bar_x > 0 and not (bar_x + BAR_WIDTH < ball_position.x + ball_radius and ball_velocity.y == 0):
            bar_x -= speed

    return True

def draw_bricks(screen, blocks):
    for block in blocks:
        # Try to draw brick image, fallback to rectangle
        if block.image is not None:
            screen.blit(block.image, block.rect)
        else:
            pygame.draw.rect(screen, block.color, block.rect)


def detect_collision(ball, blocks):
    block = None
    score = 0
    block_ind = ball.collidelist(blocks)

    if block_ind != -1:
        block = blocks[block_ind]

    if block is not None:
        if ball.top >= block.rect.bottom - 2 or ball.bottom <= block.rect.top + 5:
            ball_velocity.y *= -1
        else:
            ball_velocity.x *= -1

        # Remove the block from the list of blocks
        blocks.remove(block)
        # Remove any remaining references to the hit block to make sure Python's garbage collection deletes it
        del block

        # PLAY BRICK SOUND
        if brick_sound:
            brick_sound.play()

        score = 50

    return score

def move_ball(screen, wall_rect, bar, ball, scoreboard, timer):
    # Constrain the ball to the screen bounds
    wall_check()

    if ball_velocity.y == 0:
        msg = font.render("PRESS [SPACE] TO BEGIN", True, (255, 255, 0))
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2))
        return True
    else:
        # Move the ball
        ball_position.move_towards_ip(ball_position + ball_velocity, 10)
        # Wall collision detection (inner wall - left, right, top)
        # Left wall
        if ball_position.x - ball_radius <= wall_rect.left:
            ball_velocity.x *= -1
            ball_position.x = wall_rect.left + ball_radius
            if wall_sound:
                wall_sound.play()

        # Right wall
        if ball_position.x + ball_radius >= wall_rect.right:
            ball_velocity.x *= -1
            ball_position.x = wall_rect.right - ball_radius
            if wall_sound:
                wall_sound.play()

        # Top wall
        if ball_position.y - ball_radius <= wall_rect.top:
            ball_velocity.y *= -1
            ball_position.y = wall_rect.top + ball_radius
            if wall_sound:
                wall_sound.play()

        # Is the ball touching the paddle
        if bar.colliderect(ball):
            ball_velocity.x = get_x_angle(bar, ball)
            # Send the ball back up
            ball_velocity.y *= -1
            # Nudge the ball above the paddle to avoid sticking
            ball_position.y = bar.top - ball_radius - 1
            # PLAY PADDLE SOUND
            if paddle_sound:
                paddle_sound.play()

        if ball_position.y - ball_radius > SCREEN_HEIGHT:
            return False
        return True


def wall_check():
    global ball_velocity

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

def get_x_angle(bar, ball):
    # Calculate where on the paddle the ball collided. Invert it so positive offset is right and negative is left
    ball_offset = (bar.centerx - ball.centerx) * -1
    # Using the max x velocity, determine how much weight to apply to the offset to set an appropriate x speed
    ratio = ball_max_velocity_x / (BAR_WIDTH / 2)
    # Set the x velocity based on the offset and ratio
    return ball_offset * ratio

def update_scoreboard(screen, scoreboard, timer):
    global ball_position, ball_velocity, bar_x
    scoreboard.lose_life()
    lose_life_sound.play()
    timer.pause()  # pause timer when a life is lost

    if scoreboard.lives > 0:
        # Reset ball and paddle
        ball_position = pygame.Vector2(SCREEN_WIDTH // 2, bar_y - ball_radius - 1)
        bar_x = (SCREEN_WIDTH - BAR_WIDTH) // 2
        ball_velocity.x = 0
        ball_velocity.y = 0

        # Show "Life lost" message and wait 3 seconds
        message = font.render(f"Lives Left: {scoreboard.lives}", True, WHITE)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        return True
    else:
        timer.pause()  # stop timer on final life loss
        # Out of lives, end game
        return False

def set_win():
    global win
    win = True

def pause_game(screen):
    global pause_requested

    snapshot = screen.copy()
    choice = pause_overlay(snapshot)
    if choice == "menu":
        return False
    pygame.event.clear()
    pause_requested = False
    return True

def play(screen, debug_mode=False):
    return main_controller(screen, debug_mode)

if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    main_controller(pygame.display.set_mode((common.SCREEN_WIDTH, common.SCREEN_HEIGHT)))
