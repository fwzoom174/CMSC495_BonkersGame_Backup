# FILE STRUCTURE
# 1. Imports
# 2. Settings & Globals
# 3. Game Setup
# 4. Game Flow
# 5. Core Game Loop
# 6. Movement & Physics
# 7. Collision & Drops
# 8. Powerups
# 9. UI & Drawing
# 10. Game State
# 11. Helpers


# ================= Imports =================

# --- Standard Library ---
import os
import json
import random

# --- Third Party ---
import pygame
from pygame.mixer import Sound

# --- Game Shared Data ---
from common import (
    BLACK, WHITE, RED, COLORS,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ROOT_PATH
)

# --- Game Objects ---
from objects.block import Block
from objects.scoreboard import ScoreBoard
from objects.timer import Timer
from objects.particle import Particle
from objects.coin import Coin
from objects.powerup import PowerUp, BlueBlast

# --- Game Scenes ---
from scenes.win_lose import end_screen
from scenes.pause_overlay import pause_overlay
from scenes.levels import (
    get_level_count,
    get_level_pattern,
    get_level_settings
)

# ================= Settings & Globals =================

# --- Screen + Layout ---
WALL_PADDING = 30
WALL_TOP_PADDING = 120
BRICKS_TOP = 140

# --- Paddle + Ball Settings ---
BAR_WIDTH = 200
BAR_HEIGHT = 20
original_paddle_width = 200
small_paddle_width = 100
big_paddle_width = 280

ball_radius = 0
ball_max_velocity_x = 0

# --- Powerups ---
blast_active = False
blast_timer = 0
blast_duration = 300

paddle_shrink_active = False
paddle_shrink_timer = 0
paddle_shrink_duration = 300

paddle_big_active = False
paddle_big_timer = 0
paddle_big_duration = 300

balls = []
ball_image = None

# --- Debug + Tutorial ---
debug_countdown_mode = False

# ---- Load config ----
config_path = os.path.join(ROOT_PATH, "config.json")

if os.path.exists(config_path):
    with open(config_path, "r") as f:
        cfg = json.load(f)

    # ensure key exists
    cfg.setdefault("tutorial_enabled", True)

else:
    cfg = {"tutorial_enabled": True}
    with open(config_path, "w") as f:
        json.dump(cfg, f, indent=2)

# Tutorial state
tutorial_active = cfg["tutorial_enabled"]
tutorial_timer = 0
tutorial_phase = "move"

# --- Assets + Timers ---
pixel_font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
font = None

clock = pygame.time.Clock()
delta_time = 0

pause_requested = False
win = None
game_timer = None
level_timer = None

show_fps = False

wall_sound = None
paddle_sound = None
brick_sound = None
lose_life_sound = None

paddle_image = None
background = None

bar_x = 0
bar_y = 0
speed = 0

pygame.mixer.init()

# --- Drop Rates ---
DROP_TABLE = {
    "coin": 0.30,
    "triple_ball": 0.15,
    "blast": 0.10,
    "small_paddle": 0.05,
    "big_paddle": 0.10,
    "nothing": 0.30
}


# ================= Game Setup =================

# --- Init ---
def init(character_image=None):
    global bar_x, bar_y, speed, ball_radius, ball_position, \
        ball_velocity, ball_max_velocity_x, clock, delta_time, pause_requested, win, balls, font

    # Initialize font (must be after pygame.init())
    font = pygame.font.Font(pixel_font_path, 36)

    # Reset ball list every new game
    balls = []

    bar_x = (SCREEN_WIDTH - BAR_WIDTH) // 2
    bar_y = SCREEN_HEIGHT - BAR_HEIGHT - 100
    speed = 8

    ball_radius = 10

    
    # Load selected character image
    global ball_image
    if character_image:
        try:
            full_path = os.path.join(ROOT_PATH, character_image)
            ball_image = pygame.image.load(full_path)
            ball_image = pygame.transform.scale(ball_image, (ball_radius * 2, ball_radius * 2))
        except Exception as e:
            print(f"Error loading ball image at {character_image}: {e}")
            ball_image = None
    else:
        ball_image = None

    ball_position = pygame.Vector2(SCREEN_WIDTH // 2, bar_y - ball_radius - 4)
    ball_velocity = pygame.Vector2(0, 0)
    ball_max_velocity_x = 6

    clock = pygame.time.Clock()
    delta_time = 0
    pause_requested = False
    win = None

    load_assets()


# --- Assets ---
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


# ================= Game Flow =================

# --- Public Entry Point ---
def play(screen, debug_mode="", character_image=None):
    return main_controller(screen, debug_mode, character_image)


# --- Main Controller ---
def main_controller(screen, debug_mode="", character_image=None):
    global game_timer, level_timer

    init(character_image)
    pygame.mouse.set_visible(False)

    # ---- Reset tutorial state each time a new game starts ----
    global tutorial_active, tutorial_timer, tutorial_phase, cfg

    tutorial_timer = 0
    tutorial_phase = "move"

    # Reload config fresh when starting a new game
    config_path = os.path.join(ROOT_PATH, "config.json")
    with open(config_path, "r") as f:
        cfg = json.load(f)

    tutorial_active = cfg.get("tutorial_enabled", True)

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

    global debug_countdown_mode

    if debug_mode == "one_block":
        level = 0
        max_levels = 0
        scoreboard.lives = 1
        debug_countdown_mode = False

    elif debug_mode == "countdown":
        level = 0
        max_levels = 0
        scoreboard.lives = 1
        debug_countdown_mode = True
        level_timer = Timer(screen, mode="countdown", countdown_time=10)
        pygame.display.set_caption("Breakout Game [COUNTDOWN]")

    # --- Timer setup based on level settings ---
    settings = get_level_settings(level)

    # Always reset stopwatch when starting a new game
    game_timer = Timer(screen, mode="stopwatch")

    # Create boss countdown timer only for countdown levels
    if settings["timer"] == "countdown":
        level_timer = Timer(screen, mode="countdown", countdown_time=settings.get("time_limit", 60))
    else:
        level_timer = None

    if debug_mode == "countdown":
        pygame.display.set_caption("Breakout Game [COUNTDOWN]")
        level_timer = Timer(screen, mode="countdown", countdown_time=10)
        level = 0
        max_levels = 0

    blocks = define_blocks(screen, level)
    draw_bricks(screen, blocks)
    particles = []
    coins = []
    powerups = []
    blasts = []

    # Reset tutorial based on saved setting
    tutorial_active = cfg.get("tutorial_enabled", True)
    tutorial_timer = 0
    tutorial_phase = "move"

    # Reset power-ups at start of game
    global blast_active, blast_timer, paddle_shrink_active, paddle_shrink_timer
    blast_active = False
    blast_timer = 0
    paddle_shrink_active = False
    paddle_shrink_timer = 0

    running = True
    while running:
        status = game_loop(screen, scoreboard, game_timer, blocks, debug_mode, level, particles, coins, powerups, blasts, blast_duration)


        if status == "running":
            continue

        if status == "quit":
            running = False

        elif status == "game_over":
            running = False

        elif status == "level_complete":
            # For one_block debug, treat level clear as a simple win and exit
            if debug_mode == "one_block":
                if isinstance(game_timer, Timer):
                    game_timer.pause()

                if isinstance(level_timer, Timer):
                    level_timer.pause()
                set_win(True)
                running = False
            else:
                show_level_complete(screen, level)
                level += 1

                if level > max_levels:
                    if isinstance(game_timer, Timer):
                        game_timer.pause()
                    if isinstance(level_timer, Timer):
                        level_timer.pause()
                    set_win(True)
                    running = False
                else:
                    # Clear any leftover effects and drops before the next level
                    particles.clear()
                    coins.clear()
                    powerups.clear()
                    blasts.clear()

                    # Reset active power-up states
                    blast_active = False
                    blast_timer = 0
                    paddle_shrink_active = False
                    paddle_shrink_timer = 0

                    # Force paddle full size and recenter after level transition
                    draw_bar.width = original_paddle_width
                    draw_bar.stored_width = original_paddle_width
                    bar_x = (SCREEN_WIDTH - original_paddle_width) // 2

                    reset_ball_and_paddle()
                    blocks = define_blocks(screen, level)
                    # Timers will resume when SPACE is pressed

                    # Reconfigure level timer for new level
                    settings = get_level_settings(level)
                    if settings["timer"] == "countdown":
                        level_timer = Timer(screen, mode="countdown", countdown_time=settings.get("time_limit", 60))
                    else:
                        level_timer = None

                    # Show boss intro only when entering level 5
                    if level == 5:
                        show_boss_intro(screen)

    replay = False
    if win is not None:
        replay, initials = end_screen(screen, win, scoreboard.score)
        scoreboard.save_high_score(initials=initials, current_time=game_timer.get_time())

    return replay


# ================= Core Game Loop =================

def game_loop(screen, scoreboard, game_timer_ref, blocks, debug_mode, level, particles, coins, powerups, blasts, blast_duration):
    global ball_position, pause_requested, delta_time, blast_active, blast_timer
    global paddle_shrink_active, paddle_shrink_timer
    global paddle_big_active, paddle_big_timer
    global level_timer, ball_image

    walls = draw_wall(screen)
    bar = draw_bar(screen)
    draw_level(screen, level)

    for b in balls:
        # Draw character image if loaded, otherwise draw white circle
        if ball_image:
            screen.blit(ball_image, (int(b["pos"].x) - ball_radius, int(b["pos"].y) - ball_radius))
        else:
            pygame.draw.circle(screen, WHITE, (int(b["pos"].x), int(b["pos"].y)), ball_radius)

    scoreboard.draw()

    # ---------- TIMER DISPLAY ----------
    if isinstance(level_timer, Timer):
        level_timer.draw()
    elif isinstance(game_timer_ref, Timer):
        game_timer_ref.draw()

    # ---------- INPUT ----------
    if not balls:
        reset_ball_and_paddle()

    if not handle_input(bar, balls[0]):
        return "quit"

    draw_bricks(screen, blocks)
    scoreboard.score += detect_collision(blocks, particles, coins, powerups, scoreboard)

    # ---------- Tutorial Phase Control ----------
    global tutorial_active, tutorial_timer, tutorial_phase

    if tutorial_active:
        tutorial_timer += delta_time

        if tutorial_timer < 2500:
            tutorial_phase = "move"
            show_tutorial_phase(screen, tutorial_phase)
        elif tutorial_timer < 5000:
            tutorial_phase = "pause"
            show_tutorial_phase(screen, tutorial_phase)
        elif tutorial_timer < 7500:
            tutorial_phase = "launch"
            show_tutorial_phase(screen, tutorial_phase)
        else:
            tutorial_active = False

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
            elif powerup.type == "triple_ball":
                spawn_triple_ball()
            elif powerup.type == "big_paddle":
                paddle_big_active = True
                paddle_big_timer = paddle_big_duration
                pass
            if coin_sound:
                coin_sound.play()
    # Auto-shoot blasts when active
    if blast_active and blast_timer > 0:
        blast_timer -= 1

        # Shoot a blast every 10 frames (0.16 seconds)
        if blast_timer % 10 == 0:
            if blast_timer % 20 == 0:
                blasts.append(BlueBlast(bar.left + 2, bar.top - 20))  # Left
            else:
                blasts.append(BlueBlast(bar.right - 22, bar.top - 20))  # Right
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

    # Handle big paddle
    if paddle_big_active and paddle_big_timer > 0:
        paddle_big_timer -= 1
    if paddle_big_active and paddle_big_timer <= 0:
        paddle_big_active = False

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
                destroyed = block.hit()

                if destroyed:
                    # Create particles when brick breaks
                    for _ in range(15):
                        particles.append(Particle(block.rect.centerx, block.rect.centery, block.color))

                    # Use drop table for blast hits
                    drop = choose_drop()

                    if drop == "coin":
                        coins.append(Coin(block.rect.centerx - 15, block.rect.centery))

                    elif drop == "blast":
                        powerups.append(PowerUp(block.rect.centerx - 15, block.rect.centery, "blast"))

                    elif drop == "triple_ball":
                        powerups.append(PowerUp(block.rect.centerx - 15, block.rect.centery, "triple_ball"))

                    elif drop == "small_paddle":
                        powerups.append(PowerUp(block.rect.centerx - 15, block.rect.centery, "small_paddle"))

                    elif drop == "big_paddle":
                        powerups.append(PowerUp(block.rect.centerx - 15, block.rect.centery, "big_paddle"))

                    blocks.remove(block)
                    scoreboard.add_points(50)

                    if isinstance(brick_sound, Sound):
                        brick_sound.play()

                blasts.remove(blast)
                break

    if len(blocks) == 0:
        if isinstance(game_timer, Timer):
            game_timer.pause()
        if isinstance(level_timer, Timer):
            level_timer.pause()
        return "level_complete"

    if not move_ball(screen, walls, bar, balls):
        if not update_scoreboard(screen, scoreboard, game_timer_ref, blasts, coins, powerups):
            return "game_over"

    # --- End game if countdown expires ---
    if level_timer and level_timer.get_time() <= 0:
        if isinstance(level_timer, Timer):
            level_timer.pause()
        if isinstance(game_timer, Timer):
            game_timer.pause()
        set_win(False)
        return "game_over"

    # --- Pause / Resume ---
    if pause_requested:
        if isinstance(game_timer, Timer):
            game_timer.pause()
        if isinstance(level_timer, Timer):
            level_timer.pause()

        paused = pause_game(screen)

        pause_requested = False

        if not paused:
            return "quit"

        # resume timers
        if isinstance(game_timer, Timer):
            game_timer.resume()
        if isinstance(level_timer, Timer):
            level_timer.resume()

    # --- Update active timers ---
    if isinstance(game_timer, Timer):
        game_timer.update()
    if isinstance(level_timer, Timer):
        level_timer.update()

    # ---------- Debug FPS ----------q
    if show_fps:
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 0))

        # Bottom center of the screen
        fps_rect = fps_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        screen.blit(fps_text, fps_rect)

    pygame.display.flip()

    delta_time = clock.tick(60)
    return "running"


def define_blocks(screen, level, wall_padding=WALL_PADDING):
    global debug_countdown_mode

    blocks = []
    block_width, block_height = 60, 25
    block_space = 10

    # ----- DEBUG MODE -----
    if level == 0:
        cols = 16
        row = [0] * cols

        if debug_countdown_mode:
            row[cols//2 - 1] = 1
            row[cols//2] = 1
        else:
            row[cols//2] = 1

        layout = [row]
    else:
        layout = get_level_pattern(level)

    if not layout:
        return blocks

    rows = len(layout)
    cols = len(layout[0])

    total_blocks_width = cols * block_width + (cols - 1) * block_space
    left_offset = (SCREEN_WIDTH - total_blocks_width) // 2

    # ----- PLACE BLOCKS -----
    for row_index, row in enumerate(layout):
        for col_index, cell in enumerate(row):

            if cell == 0:
                continue

            block_x = left_offset + col_index * (block_width + block_space)
            block_y = BRICKS_TOP + (block_height * row_index) + (block_space * row_index)

            # normal number mode
            if isinstance(cell, int):
                block_type = cell
                color = COLORS[row_index % len(COLORS)]

            # tuple mode (type, color)
            elif isinstance(cell, (tuple, list)):
                block_type = cell[0]
                color_index = cell[1] % len(COLORS)
                color = COLORS[color_index]
            else:
                continue

            # square block center shift
            if block_type == 2:
                block_x += (block_width - 35) // 2
                block_y += (block_height - 35) // 2

            blocks.append(Block(block_x, block_y, color, block_type))

    return blocks


def reset_ball_and_paddle():
    global balls, bar_x
    global paddle_shrink_active, paddle_shrink_timer
    global paddle_big_active, paddle_big_timer
    global blast_active, blast_timer

    # Reset paddle powerups
    paddle_shrink_active = False
    paddle_shrink_timer = 0
    paddle_big_active = False
    paddle_big_timer = 0
    blast_active = False
    blast_timer = 0

    # Reset paddle width animation
    draw_bar.width = original_paddle_width
    draw_bar.stored_width = original_paddle_width

    # Reset paddle to center
    bar_x = (SCREEN_WIDTH - original_paddle_width) // 2

    # ---- Reset BALLS the correct way ----
    balls = [
        {
            "pos": pygame.Vector2(SCREEN_WIDTH // 2, bar_y - ball_radius - 4),
            "vel": pygame.Vector2(0, 0)
        }
    ]


def handle_input(bar, main_ball):
    global pause_requested, bar_x, tutorial_active

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:

            # -------- Always Allow Pause (tutorial or normal) --------
            if event.key == pygame.K_ESCAPE:
                pause_requested = True
                return True

            # -------- Tutorial Controls --------
            if tutorial_active and event.key == pygame.K_SPACE:

                tutorial_active = False

                # Launch ball
                balls[0]["vel"].x = get_x_angle(bar, balls[0])
                balls[0]["vel"].y = -5

                # Resume timers
                if isinstance(game_timer, Timer):
                    if game_timer.start_time is None:
                        game_timer.start()
                    else:
                        game_timer.resume()

                if isinstance(level_timer, Timer):
                    if level_timer.start_time is None:
                        level_timer.start()
                    else:
                        level_timer.resume()

                return True

            # -------- Normal Launch --------
            if event.key == pygame.K_SPACE and main_ball["vel"].length() == 0:

                # center ball if aligned close enough
                bar_center = bar.centerx
                ball_center = main_ball["pos"].x

                if abs(ball_center - bar_center) < 3:
                    main_ball["pos"].x = bar_center

                # apply bounce angle
                main_ball["vel"].x = get_x_angle(bar, main_ball)
                if abs(main_ball["vel"].x) < 0.5:
                    main_ball["vel"].x = 0

                main_ball["vel"].y = -6

                # start or resume timers
                if isinstance(game_timer, Timer):
                    if game_timer.start_time is None:
                        game_timer.start()
                    else:
                        game_timer.resume()

                if isinstance(level_timer, Timer):
                    if level_timer.start_time is None:
                        level_timer.start()
                    else:
                        level_timer.resume()

                return True

    # -------- Paddle Movement --------
    keys = pygame.key.get_pressed()
    paddle_width = small_paddle_width if paddle_shrink_active else BAR_WIDTH

    if main_ball["vel"].length() == 0:
        ball_x = main_ball["pos"].x

        left_limit = int(ball_x - (paddle_width - ball_radius * 2))
        right_limit = int(ball_x - ball_radius * 2)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            bar_x = max(bar_x - speed, left_limit)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            bar_x = min(bar_x + speed, right_limit)
    else:
        edge_adjust = 8

        min_x = WALL_PADDING - edge_adjust
        max_x = SCREEN_WIDTH - WALL_PADDING - paddle_width + edge_adjust

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            bar_x = max(bar_x - speed, min_x)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            bar_x = min(bar_x + speed, max_x)

    return True


# ================= Movement & Physics =================

def move_ball(screen, walls, bar, balls_list):
    if balls_list[0]["vel"].length() == 0:
        if not tutorial_active:
            msg = font.render("PRESS [SPACE] TO BEGIN", True, (255, 255, 0))
            screen.blit(
                msg,
                (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2)
            )
        return True

    # --- After launch: move each active ball ---
    for b in balls_list[:]:
        # Move ball
        steps = 3
        for _ in range(steps):
            b["pos"] += b["vel"] / steps

        # Wall and paddle collision for each ball
        wall_check_multi(b, walls)
        paddle_check_multi(b, bar)

        # If ball exits the screen, remove it
        if b["pos"].y - ball_radius > SCREEN_HEIGHT:
            balls_list.remove(b)

    # If no balls remain after removals → life lost
    return len(balls_list) > 0


def wall_check_multi(ball, walls):
    hit_wall = False

    if ball["pos"].x - ball_radius <= walls.left:
        ball["vel"].x *= -1
        ball["pos"].x = walls.left + ball_radius
        hit_wall = True

    elif ball["pos"].x + ball_radius >= walls.right:
        ball["vel"].x *= -1
        ball["pos"].x = walls.right - ball_radius
        hit_wall = True

    if ball["pos"].y - ball_radius <= walls.top:
        ball["vel"].y *= -1
        ball["pos"].y = walls.top + ball_radius
        hit_wall = True

    if hit_wall and wall_sound:
        wall_sound.play()


# ---------- Paddle Collision ----------
def paddle_check_multi(ball, bar):
    ball_rect = pygame.Rect(
        ball["pos"].x - ball_radius,
        ball["pos"].y - ball_radius,
        ball_radius * 2,
        ball_radius * 2
    )

    if bar.colliderect(ball_rect) and ball["vel"].y > 0:
        ball["vel"].x = get_x_angle(bar, ball)

        if abs(ball["vel"].x) < 0.2:
            ball["vel"].x = 0

        ball["vel"].y *= -1
        ball["pos"].y = bar.top - ball_radius - 1

        if isinstance(paddle_sound, Sound):
            paddle_sound.play()


def get_x_angle(bar, ball_dict):
    ball_center_x = ball_dict["pos"].x
    bar_center_x = bar.centerx
    offset = ball_center_x - bar_center_x
    ratio = ball_max_velocity_x / (bar.width / 2)
    return offset * ratio


# ================= Collision & Drops =================

def detect_collision(blocks, particles, coins, powerups, scoreboard):
    global balls, blast_active, paddle_shrink_active

    score_increase = 0

    for ball in balls[:]:
        ball_rect = pygame.Rect(ball["pos"].x - ball_radius, ball["pos"].y - ball_radius, ball_radius*2, ball_radius*2)
        block_index = ball_rect.collidelist(blocks)

        if block_index != -1:
            block = blocks[block_index]

            # ---- COLLISION ANGLE CALCULATION (same as original behavior) ----
            if abs(ball_rect.bottom - block.rect.top) < 8 and ball["vel"].y > 0:
                ball["vel"].y *= -1
            elif abs(ball_rect.top - block.rect.bottom) < 8 and ball["vel"].y < 0:
                ball["vel"].y *= -1
            elif abs(ball_rect.right - block.rect.left) < 8 and ball["vel"].x > 0:
                ball["vel"].x *= -1
            elif abs(ball_rect.left - block.rect.right) < 8 and ball["vel"].x < 0:
                ball["vel"].x *= -1
            else:
                ball["vel"].y *= -1

            # ---- BLOCK HP LOGIC ----
            destroyed = block.hit()

            if destroyed:
                # particles same as before
                for _ in range(15):
                    particles.append(Particle(block.rect.centerx, block.rect.centery, block.color))

                drop = choose_drop()

                if drop == "coin":
                    coins.append(Coin(block.rect.centerx - 15, block.rect.centery))

                elif drop == "blast":
                    powerups.append(PowerUp(block.rect.centerx - 15, block.rect.centery, "blast"))

                elif drop == "triple_ball":
                    powerups.append(PowerUp(block.rect.centerx - 15, block.rect.centery, "triple_ball"))

                elif drop == "small_paddle":
                    powerups.append(PowerUp(block.rect.centerx - 15, block.rect.centery, "small_paddle"))

                elif drop == "big_paddle":
                    powerups.append(PowerUp(block.rect.centerx - 15, block.rect.centery, "big_paddle"))

                # remove block after effects
                blocks.remove(block)

                # sound
                if isinstance(brick_sound, Sound):
                    brick_sound.play()

                score_increase += 50

    return score_increase


def choose_drop():
    roll = random.random()
    total = 0

    for item, chance in DROP_TABLE.items():
        total += chance
        if roll < total:
            return item

    return "nothing"


# ================= Powerups =================

def spawn_triple_ball():
    global balls

    if len(balls) == 0:
        return

    base = balls[0]
    new_velocity = abs(base["vel"].x or 3)

    balls.append({"pos": base["pos"].copy(), "vel": pygame.Vector2(-new_velocity, -5)})
    balls.append({"pos": base["pos"].copy(), "vel": pygame.Vector2(new_velocity, -5)})


# ================= UI & Drawing =================

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
    global bar_x, paddle_shrink_active

    if paddle_shrink_active:
        target_width = small_paddle_width
    elif paddle_big_active:
        target_width = big_paddle_width
    else:
        target_width = original_paddle_width

    current_width = getattr(draw_bar, "width", original_paddle_width)
    current_width += (target_width - current_width) * 0.10
    draw_bar.width = current_width

    # --- Centering fix ---
    old_width = getattr(draw_bar, "stored_width", original_paddle_width)
    width_change = current_width - old_width
    bar_x -= width_change / 2
    draw_bar.stored_width = current_width

    bar = pygame.Rect(bar_x, bar_y, current_width, BAR_HEIGHT)
    image_y_offset = -11

    if paddle_image:
        scaled_paddle = pygame.transform.scale(paddle_image, (int(current_width), BAR_HEIGHT))
        screen.blit(scaled_paddle, (bar_x, bar_y + image_y_offset))
    else:
        pygame.draw.rect(screen, RED, bar)

    return bar


# ---------- Block Drawing ----------
def draw_bricks(screen, blocks):
    for block in blocks:
        if block.image is not None:
            screen.blit(block.image, block.rect)
        else:
            pygame.draw.rect(screen, block.color, block.rect)


def draw_level(screen, level):
    text = font.render(f"LEVEL {level}", True, (255, 255, 0))
    rect = text.get_rect(center=(SCREEN_WIDTH // 2, WALL_TOP_PADDING - 40))
    screen.blit(text, rect)


# ---------- Tutorial Phase ----------
def show_tutorial_phase(screen, phase):
    tutorial_path = os.path.join(ROOT_PATH, "media", "graphics", "tutorial")

    arrow_img = pygame.image.load(os.path.join(tutorial_path, "arrow_keys.png"))
    wasd_img = pygame.image.load(os.path.join(tutorial_path, "wasd_keys.png"))
    esc_img = pygame.image.load(os.path.join(tutorial_path, "Esc Key.png"))
    space_img = pygame.image.load(os.path.join(tutorial_path, "Space Bar.png"))

    arrow_img = pygame.transform.scale(arrow_img, (140, 140))
    wasd_img = pygame.transform.scale(wasd_img, (140, 140))
    esc_img = pygame.transform.scale(esc_img, (140, 140))
    space_img = pygame.transform.scale(space_img, (260, 80))

    font_path = os.path.join(ROOT_PATH, "media", "graphics", "font", "Pixeboy.ttf")
    font = pygame.font.Font(font_path, 42)
    label_font = pygame.font.Font(font_path, 28)

    if phase == "move":
        arrow_pos = (SCREEN_WIDTH // 2 - 180, 290)
        wasd_pos = (SCREEN_WIDTH // 2 + 40, 290)

        # draw icons only
        screen.blit(arrow_img, arrow_pos)
        screen.blit(wasd_img, wasd_pos)

        # bottom text
        text = font.render("Use ARROW KEYS or A/D to move", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 460))

    if phase == "pause":
        esc_pos = (SCREEN_WIDTH // 2 - 70, 290)
        screen.blit(esc_img, esc_pos)

        text = font.render("Press ESC to pause the game", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 460))

    if phase == "launch":
        space_pos = (SCREEN_WIDTH // 2 - 130, 320)
        screen.blit(space_img, space_pos)

        text = font.render("Press SPACE to launch the ball", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 460))


def show_level_complete(screen, level):
    message = font.render(f"LEVEL {level} COMPLETE!", True, (255, 255, 0))
    message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(message, message_rect)
    pygame.display.flip()
    pygame.time.wait(1000)


def show_boss_intro(screen):
    font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
    big_font = pygame.font.Font(font_path, 76)
    small_font = pygame.font.Font(font_path, 36)

    lines = [
        "FINAL LEVEL!",
        "THE BOSS AWAITS.",
        "You have 1 minute to destroy all bricks.",
        "Press SPACE to begin..."
    ]

    screen.fill((0, 0, 0))  # full black screen

    y = SCREEN_HEIGHT // 2 - 120
    for i, text in enumerate(lines):
        font = big_font if i == 0 else small_font
        surf = font.render(text, True, (255, 255, 255))
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(surf, rect)
        y += 70

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False


# ================= Game State =================

def update_scoreboard(screen, scoreboard, timer, blasts, coins, powerups):
    global ball_position, ball_velocity, bar_x
    global blast_active, blast_timer
    global paddle_shrink_active, paddle_shrink_timer
    global paddle_big_active, paddle_big_timer

    scoreboard.lose_life()
    if isinstance(lose_life_sound, Sound):
        lose_life_sound.play()

    if isinstance(game_timer, Timer):
        game_timer.pause()
    if isinstance(level_timer, Timer):
        level_timer.pause()

    if scoreboard.lives > 0:
        reset_ball_and_paddle()

        # Reset power-ups when losing a life
        blast_active = False
        blast_timer = 0
        paddle_shrink_active = False
        paddle_shrink_timer = 0
        paddle_big_active = False
        paddle_big_timer = 0

        # Clear all falling items
        blasts.clear()
        coins.clear()
        powerups.clear()

        message = font.render(f"Lives Left: {scoreboard.lives}", True, WHITE)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        return True

    # ---------- No lives left → GAME OVER ----------
    if isinstance(game_timer, Timer):
        game_timer.pause()
    if isinstance(level_timer, Timer):
        level_timer.pause()

    set_win(False)
    return False


def set_win(state=True):
    global win
    win = state


def pause_game(screen):
    global pause_requested
    # --- Update active timers ---
    if isinstance(game_timer, Timer):
        game_timer.update()
    if isinstance(level_timer, Timer):
        level_timer.update()

    snapshot = screen.copy()
    choice = pause_overlay(snapshot)
    if choice == "menu":
        pygame.mouse.set_visible(True)
        return False