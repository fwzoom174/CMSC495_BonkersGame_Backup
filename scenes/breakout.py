import pygame
from pygame.mixer import Sound

import os

from common import BLACK, WHITE, RED, COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, ROOT_PATH
from objects.block import Block
from objects.scoreboard import ScoreBoard
from scenes.win_lose import end_screen
from objects.timer import Timer
from scenes.pause_overlay import pause_overlay
from scenes.levels import get_level_count, get_level_pattern
from objects.particle import Particle
from objects.coin import Coin
from objects.powerup import PowerUp, BlueBlast
import random

WALL_PADDING = 30
WALL_TOP_PADDING = 120
BRICKS_TOP = 140

pixel_font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
font = pygame.font.Font(pixel_font_path, 36)

BAR_WIDTH = 200
BAR_HEIGHT = 20
bar_x = 0
bar_y = 0
speed = 0

ball_radius = 0
ball_position = pygame.Vector2(0, 0)
ball_velocity = pygame.Vector2(0, 0)
ball_max_velocity_x = 0
blast_active = False
blast_timer = 0
blast_duration = 300
paddle_shrink_active = False
paddle_shrink_timer = 0
paddle_shrink_duration = 300  
original_paddle_width = 200
small_paddle_width = 100

clock = pygame.time.Clock()
delta_time = 0
pause_requested = False
win = None

#FPS toggle
show_fps = False

wall_sound = None
paddle_sound = None
brick_sound = None
lose_life_sound = None

paddle_image = None
background = None

pygame.mixer.init()


def init():
    global bar_x, bar_y, speed, ball_radius, ball_position, \
        ball_velocity, ball_max_velocity_x, clock, delta_time, pause_requested, win

    bar_x = (SCREEN_WIDTH - BAR_WIDTH) // 2
    bar_y = SCREEN_HEIGHT - BAR_HEIGHT - 100
    speed = 7

    ball_radius = 10
    ball_position = pygame.Vector2(SCREEN_WIDTH // 2, bar_y - ball_radius - 4)
    ball_velocity = pygame.Vector2(0, 0)
    ball_max_velocity_x = 5

    clock = pygame.time.Clock()
    delta_time = 0
    pause_requested = False
    win = None

    load_assets()


def load_assets():
    global wall_sound, paddle_sound, brick_sound, lose_life_sound, coin_sound, blast_shoot_sound, paddle_image, background

    try:
        wall_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_wall-hit.wav'))
        paddle_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_paddle-hit.wav'))
        brick_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_brick-hit.ogg'))
        lose_life_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_lose-lives.wav'))
        coin_sound = Sound(os.path.join(ROOT_PATH, "media", "audio", "media_audio_collect_coin.ogg"))
        blast_shoot_sound = pygame.mixer.Sound(os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_blast_shoot.wav'))
    except FileNotFoundError:
        print("Warning: Could not load sound files. Game will run without sound.")

    try:
        paddle_image = pygame.image.load(os.path.join(ROOT_PATH, 'media', 'graphics', 'paddle', 'paddle.png'))
        paddle_image = pygame.transform.scale(paddle_image, (BAR_WIDTH, BAR_HEIGHT))
    except FileNotFoundError:
        print("Warning: Could not load paddle image")

    try:
        background = pygame.image.load(
            os.path.join(ROOT_PATH, 'media', 'graphics', 'background', 'back-black-wall-border.png'))
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except FileNotFoundError:
        print("Warning: Could not load background image. Using black background.")


def main_controller(screen, debug_mode=""):
    init()
    # Default level
    level = 1

    # Debug level start shortcuts
    if debug_mode == "level_1":
        level = 1
    elif debug_mode == "level_2":
        level = 2
    elif debug_mode == "level_3":
        level = 3
    elif debug_mode == "level_4":
        level = 4
    elif debug_mode == "level_5":
        level = 5

    max_levels = get_level_count()

    pygame.display.set_caption("Breakout Game")
    scoreboard = ScoreBoard(screen)

    # Turn on FPS when entering a debug mode game
    global show_fps
    show_fps = debug_mode is not False

    if debug_mode == "one_block":
        # Special debug mode: single block, no level progression
        level = 0
        max_levels = 0
        scoreboard.lives = 1

    timer = Timer(screen, mode="stopwatch")
    if debug_mode == "countdown":
        timer = Timer(screen, mode="countdown", countdown_time=10)

    blocks = define_blocks(screen, level)
    draw_bricks(screen, blocks)
    particles = []
    coins = []
    powerups = []
    blasts = []
  

    running = True
    while running:
        status = game_loop(screen, scoreboard, timer, blocks, debug_mode, level, particles, coins, powerups, blasts, blast_duration)

        if status == "running":
            continue

        if status == "quit":
            running = False

        elif status == "game_over":
            running = False

        elif status == "level_complete":
            # For one_block debug, treat level clear as a simple win and exit
            if debug_mode == "one_block":
                timer.pause()
                set_win(True)
                running = False
            else:
                show_level_complete(screen, level)
                level += 1

                if level > max_levels:
                    timer.pause()
                    set_win(True)
                    running = False
                else:
                    reset_ball_and_paddle()
                    blocks = define_blocks(screen, level)
                    # Timer is already paused; it will resume when SPACE is pressed

    replay = False
    if win is not None:
        replay, initials = end_screen(screen, win, scoreboard.score)
        scoreboard.save_high_score(initials=initials, current_time=timer.get_time())

    return replay

# ---------- Block Layout ----------
def define_blocks(screen, level, wall_padding=WALL_PADDING):
    blocks = []
    block_width, block_height = 60, 25
    block_space = 10

    # Debug level: single block in the normal grid layout
    if level == 0:
        num_blocks = 1
        row = column = 0

        usable_width = screen.get_width() - (wall_padding * 2)
        blocks_per_row = (usable_width + block_space) // (block_width + block_space)

        total_blocks_width = blocks_per_row * block_width + (blocks_per_row - 1) * block_space
        left_offset = (screen.get_width() - total_blocks_width) // 2

        for i in range(num_blocks):
            if column >= blocks_per_row:
                row += 1
                column = 0

            block_x = left_offset + column * (block_width + block_space)
            block_y = BRICKS_TOP + (block_height * row) + (block_space * row)

            color = COLORS[row % len(COLORS)]
            blocks.append(Block(pygame.Rect(block_x, block_y, block_width, block_height), color))
            column += 1

        return blocks

    # Normal levels: use layouts from scenes.levels
    layout = get_level_pattern(level)
    if not layout:
        return blocks

    rows = len(layout)
    cols = len(layout[0]) if rows > 0 else 0
    if cols == 0:
        return blocks

    total_blocks_width = cols * block_width + (cols - 1) * block_space
    left_offset = (screen.get_width() - total_blocks_width) // 2

    for row_index, row in enumerate(layout):
        for col_index, cell in enumerate(row):

            # Skip empty spaces
            if cell == 0:
                continue

            block_x = left_offset + col_index * (block_width + block_space)
            block_y = BRICKS_TOP + (block_height * row_index) + (block_space * row_index)


            # CASE 1 — old system (1 or 2)
            if isinstance(cell, int):
                block_type = cell
                color = COLORS[row_index % len(COLORS)]

            # CASE 2 — (type, colorIndex)
            elif isinstance(cell, (tuple, list)):
                block_type = cell[0]
                color_index = cell[1] % len(COLORS)
                color = COLORS[color_index]
            else:
                continue

            # -------- CENTER SQUARE BLOCKS (2 HP) --------
            if block_type == 2:
                offset_x = (block_width - 35) // 2
                offset_y = (block_height - 35) // 2
            else:
                offset_x = 0
                offset_y = 0

            block_x += offset_x
            block_y += offset_y

            # create block
            blocks.append(Block(block_x, block_y, color, block_type))

    return blocks

def game_loop(screen, scoreboard, timer, blocks, debug_mode, level, particles, coins, powerups, blasts, blast_duration):
    global ball_position, pause_requested, delta_time, blast_active, blast_timer, paddle_shrink_active, paddle_shrink_timer

    walls = draw_wall(screen)
    bar = draw_bar(screen)
    draw_level(screen, level)

    ball = pygame.draw.circle(screen, WHITE, ball_position, ball_radius)
    scoreboard.draw()
    timer.draw()

    if not handle_input(bar, ball, timer):
        return "quit"

    draw_bricks(screen, blocks)
    scoreboard.score += detect_collision(ball, blocks, particles, coins, powerups)

    # Update and draw particles
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.is_dead():
            particles.remove(particle)

    # Update and draw coins
    for coin in coins[:]:
        coin.update()
        coin.draw(screen)
        if coin.is_off_screen():
            coins.remove(coin)
    
    # Check if paddle collects coin
    for coin in coins[:]:
        if coin.rect.bottom >= bar.top and coin.rect.colliderect(bar):
            scoreboard.add_points(50)  
            coins.remove(coin)
            if coin_sound:
                coin_sound.play()

    # Update and draw powerups
    for powerup in powerups[:]:
        powerup.update()
        powerup.draw(screen)
        if powerup.is_off_screen():
                powerups.remove(powerup)

    # Check if paddle collects powerup
    for powerup in powerups[:]:
        if bar.colliderect(powerup.rect):
            powerups.remove(powerup)

            if powerup.type == "blast":
                blast_active = True
                blast_timer = blast_duration
            elif powerup.type == "small_paddle":
                paddle_shrink_active = True
                paddle_shrink_timer = paddle_shrink_duration
                pass

            if coin_sound:
                coin_sound.play()
    # Auto-shoot blasts when active
    if blast_active and blast_timer > 0:
        blast_timer -= 1
    
        # Shoot a blast every 10 frames (0.16 seconds)
        if blast_timer % 10 == 0:
            blasts.append(BlueBlast(bar.centerx - 10, bar.top - 20))
            if blast_shoot_sound:
                blast_shoot_sound.play()

    
        # Deactivate when timer runs out
        if blast_timer <= 0:
            blast_active = False

            # Handle paddle shrinking
        if paddle_shrink_active and paddle_shrink_timer > 0:
            paddle_shrink_timer -= 1
        
        if paddle_shrink_active and paddle_shrink_timer <= 0:
            paddle_shrink_active = False

    # Update and draw blasts
    for blast in blasts[:]:
        blast.update()
        blast.draw(screen)
        if blast.is_off_screen():
            blasts.remove(blast)
    
    # Check if blasts hit bricks
    for blast in blasts[:]:
        for block in blocks:
            if block.rect.colliderect(blast.rect):
                # Create particles when brick breaks
                for _ in range(15):
                    particles.append(Particle(block.rect.centerx, block.rect.centery, block.color))
                
                # 30% chance to drop a coin
                if random.random() < 0.40:
                    coins.append(Coin(block.rect.centerx - 15, block.rect.centery))
                
                # 20% chance to drop a powerup
                if random.random() < 0.20:
                    powerups.append(PowerUp(block.rect.centerx - 15, block.rect.centery))
                
                blocks.remove(block)
                blasts.remove(blast)
                scoreboard.add_points(50)
                
                if isinstance(brick_sound, Sound):
                    brick_sound.play()
                break
             

    if len(blocks) == 0:
        timer.pause()
        return "level_complete"

    if not move_ball(screen, walls, bar, ball):
        if not update_scoreboard(screen, scoreboard, timer):
            return "game_over"

    if debug_mode == "countdown" and timer.get_time() <= 0:
        set_win(False)
        return "game_over"

    if pause_requested:
        if not pause_game(screen, timer):
            return "quit"
        else:
            timer.resume()

    timer.update()

    # ---------- Debug FPS ----------
    if show_fps:
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 0))

        # Bottom center of the screen
        fps_rect = fps_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        screen.blit(fps_text, fps_rect)

    pygame.display.flip()

    delta_time = clock.tick(60)
    return "running"

# ---------- Wall ----------
def draw_wall(screen):
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BLACK)

    wall_bottom = SCREEN_HEIGHT - 150

    return pygame.Rect(
        WALL_PADDING,
        WALL_TOP_PADDING,
        SCREEN_WIDTH - WALL_PADDING * 2,
        wall_bottom - WALL_TOP_PADDING
    )

# ---------- Draw Paddle ----------
def draw_bar(screen):
    global paddle_shrink_active
    # Use small or normal paddle width
    if paddle_shrink_active:
        current_width = small_paddle_width
    else:
        current_width = original_paddle_width
    
    bar = pygame.Rect(bar_x, bar_y, current_width, BAR_HEIGHT)
    image_y_offset = -11

    if paddle_image:
        # Scale paddle image to current width
        scaled_paddle = pygame.transform.scale(paddle_image, (current_width, BAR_HEIGHT))
        screen.blit(scaled_paddle, (bar_x, bar_y + image_y_offset))
    else:
        pygame.draw.rect(screen, RED, bar)

    return bar

def draw_level(screen, level):
    text = font.render(f"LEVEL {level}", True, (255, 255, 0))
    rect = text.get_rect(center=(SCREEN_WIDTH // 2, WALL_TOP_PADDING - 40))
    screen.blit(text, rect)

def reset_ball_and_paddle():
    global ball_position, ball_velocity, bar_x
    ball_position = pygame.Vector2(SCREEN_WIDTH // 2, bar_y - ball_radius - 4)
    bar_x = (SCREEN_WIDTH - BAR_WIDTH) // 2
    ball_velocity.x = 0
    ball_velocity.y = 0

def handle_input(bar, ball, timer):
    global pause_requested, bar_x

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and ball_velocity.y == 0:
                ball_velocity.x = get_x_angle(bar, ball)
                ball_velocity.y = -5
                timer.resume()
            if event.key == pygame.K_ESCAPE:
                pause_requested = True

    keys = pygame.key.get_pressed()

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        if bar_x + BAR_WIDTH < SCREEN_WIDTH - WALL_PADDING + 2 and not (bar_x > ball_position.x - ball_radius and ball_velocity.y == 0):
            bar_x += speed

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        if bar_x > WALL_PADDING - 2 and not (bar_x + BAR_WIDTH < ball_position.x + ball_radius and ball_velocity.y == 0):
            bar_x -= speed

    return True


# ---------- Block Drawing ----------
def draw_bricks(screen, blocks):
    for block in blocks:
        if block.image is not None:
            screen.blit(block.image, block.rect)
        else:
            pygame.draw.rect(screen, block.color, block.rect)


# ---------- Block Collision ----------
def detect_collision(ball, blocks, particles, coins, powerups):
    score = 0
    block_index = ball.collidelist(blocks)

    if block_index != -1:
        block = blocks[block_index]
        ball_rect = pygame.Rect(ball)

        if abs(ball_rect.bottom - block.rect.top) < 8 and ball_velocity.y > 0:
            ball_velocity.y *= -1
        elif abs(ball_rect.top - block.rect.bottom) < 8 and ball_velocity.y < 0:
            ball_velocity.y *= -1
        elif abs(ball_rect.right - block.rect.left) < 8 and ball_velocity.x > 0:
            ball_velocity.x *= -1
        elif abs(ball_rect.left - block.rect.right) < 8 and ball_velocity.x < 0:
            ball_velocity.x *= -1
        else:
            ball_velocity.y *= -1

        # Use the Block HP logic
        should_destroy = block.hit()
        if should_destroy:
            # Create particles when brick breaks
            for _ in range(15):
                particles.append(Particle(block.rect.centerx, block.rect.centery, block.color))

            # 40% chance to drop a coin
            if random.random() < 0.40:
                coins.append(Coin(block.rect.centerx - 15, block.rect.centery))
            
            # 20% chance to drop a powerup
            if random.random() < 0.20:
                # 50/50 chance
                powerup_type = random.choice(["blast", "small_paddle"])
                powerups.append(PowerUp(block.rect.centerx - 15, block.rect.centery, powerup_type))
            
            del blocks[block_index]

            if isinstance(brick_sound, Sound):
                brick_sound.play()

            score = 50

    return score

def move_ball(screen, walls, bar, ball):
    if ball_velocity.y == 0:
        msg = font.render("PRESS [SPACE] TO BEGIN", True, (255, 255, 0))
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2))
        return True
    else:
        ball_position.move_towards_ip(ball_position + ball_velocity, 10)

        wall_check(walls)
        paddle_check(bar, ball)

        if ball_position.y - ball_radius > SCREEN_HEIGHT:
            return False
        return True


def wall_check(walls):
    global ball_velocity

    if ball_position.x - ball_radius <= walls.left:
        ball_velocity.x *= -1
        ball_position.x = walls.left + ball_radius
        if isinstance(wall_sound, Sound):
            wall_sound.play()

    if ball_position.x + ball_radius >= walls.right:
        ball_velocity.x *= -1
        ball_position.x = walls.right - ball_radius
        if isinstance(wall_sound, Sound):
            wall_sound.play()

    if ball_position.y - ball_radius <= walls.top:
        ball_velocity.y *= -1
        ball_position.y = walls.top + ball_radius
        if isinstance(wall_sound, Sound):
            wall_sound.play()


# ---------- Paddle Collision ----------
def paddle_check(bar, ball):
    if bar.colliderect(ball):
        ball_velocity.x = get_x_angle(bar, ball)
        ball_velocity.y *= -1
        ball_position.y = bar.top - ball_radius - 1

        if isinstance(paddle_sound, Sound):
            paddle_sound.play()


def get_x_angle(bar, ball):
    ball_offset = (bar.centerx - ball.centerx) * -1
    ratio = ball_max_velocity_x / (BAR_WIDTH / 2)
    return ball_offset * ratio

def update_scoreboard(screen, scoreboard, timer):
    global ball_position, ball_velocity, bar_x
    scoreboard.lose_life()
    if isinstance(lose_life_sound, Sound):
        lose_life_sound.play()

    timer.pause()

    if scoreboard.lives > 0:
        reset_ball_and_paddle()

        message = font.render(f"Lives Left: {scoreboard.lives}", True, WHITE)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        return True
    else:
        timer.pause()
        set_win(False)
        return False

def show_level_complete(screen, level):
    message = font.render(f"LEVEL {level} COMPLETE!", True, (255, 255, 0))
    message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(message, message_rect)
    pygame.display.flip()
    pygame.time.wait(1000)

def set_win(state=True):
    global win
    win = state


def pause_game(screen, timer):
    global pause_requested
    timer.pause()

    snapshot = screen.copy()
    choice = pause_overlay(snapshot)
    if choice == "menu":
        return False

    pygame.event.clear()
    pause_requested = False
    return True


def play(screen, debug_mode=""):
    return main_controller(screen, debug_mode)
