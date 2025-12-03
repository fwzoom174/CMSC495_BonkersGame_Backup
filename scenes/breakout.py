"""
Breakout Gameplay Module.

This file controls:
- game setup and reset
- game loop and flow
- physics and paddle/ball interaction
- block collision and powerup drops
- tutorials and UI drawing
- timers, win/loss logic, and scene transitions
"""

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
blast_duration = 300  # length of blast powerup

paddle_state = "normal"
paddle_state_timer = 0
paddle_power_duration = 300  # shared duration for paddle size effects

balls = []
ball_image = None
last_hit_ball = None  # remembers last ball that touched paddle for triple-ball logic

# --- Debug + Tutorial ---
debug_countdown_mode = False

# ---- Load config ----
config_path = "config.json"

# Load configuration file if it exists
if os.path.exists(config_path):
    try:
        with open(config_path, "r") as f:
            cfg = json.load(f)
    except:
        cfg = {}
else:
    cfg = {}

# Default config values
cfg.setdefault("sound_volume", 5)
cfg.setdefault("music_volume", 5)
cfg.setdefault("tutorial_enabled", True)

# Tutorial state
tutorial_active = cfg["tutorial_enabled"]
tutorial_timer = 0
tutorial_phase = "move"

# --- Assets + Timers ---
pixel_font_path = os.path.join(ROOT_PATH, 'media', 'graphics', 'font', 'Pixeboy.ttf')
font = None

clock = pygame.time.Clock()
delta_time = 0  # frame timing

pause_requested = False
win = None
game_timer = None
level_timer = None

show_fps = False  # FPS toggle

# Sound placeholders
wall_sound = None
paddle_sound = None
brick_sound = None
lose_life_sound = None
coin_sound = None
blast_shoot_sound = None
pause_sound = None
unpause_sound = None

# Images
paddle_image: pygame.Surface | None = None
background = None

# Paddle movement values
bar_x = 0
bar_y = 0
speed = 0

pygame.mixer.init()


# --- Central Volume Reader ---
def current_volume():
    """Always read fresh sound volume (0.0 – 1.0) from config.json."""
    try:
        with open("config.json","r") as f:
            c = json.load(f)
            val = c.get("sound_volume", 5)
            return max(0, min(5, val)) / 5.0
    except:
        return 1.0


# --- Drop Rates ---
DROP_TABLE = {
    "coin": 0.30,
    "triple_ball": 0.10,
    "blast": 0.10,
    "small_paddle": 0.05,
    "big_paddle": 0.10,
    "nothing": 0.35
}


# ================= Game Setup =================

def init(character_image=None):
    """Setup all initial game values and reset paddle/ball."""
    global bar_x, bar_y, speed, ball_radius, ball_position, \
        ball_velocity, ball_max_velocity_x, clock, delta_time, pause_requested, win, balls, font

    font = pygame.font.Font(pixel_font_path, 36)

    # Reset ball list every new game
    balls = []

    # Paddle placement
    bar_x = (SCREEN_WIDTH - BAR_WIDTH) // 2
    bar_y = SCREEN_HEIGHT - BAR_HEIGHT - 100
    speed = 8  # paddle move speed

    ball_radius = 10

    # Load selected character image for ball
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

    # Ball starting position
    ball_position = pygame.Vector2(SCREEN_WIDTH // 2, bar_y - ball_radius - 4)
    ball_velocity = pygame.Vector2(0, 0)
    ball_max_velocity_x = 6  # maximum sideways speed

    clock = pygame.time.Clock()
    delta_time = 0
    pause_requested = False
    win = None

    load_assets()  # load images and sounds


# ---------- Volume Helper ----------
def apply_sound_volumes():
    """Update volume levels for all loaded sound effects."""
    global cfg

    try:
        with open(config_path, "r") as f:
            cfg = json.load(f)
    except:
        cfg = {"sound_volume": 5}
    try:
        level = int(cfg.get("sound_volume", 5))
    except:
        level = 5

    level = max(0, min(5, level))
    vol = level / 5.0

    try:
        # Set volume for each sound if loaded
        if isinstance(wall_sound, Sound):
            wall_sound.set_volume(vol)
        if isinstance(paddle_sound, Sound):
            paddle_sound.set_volume(vol)
        if isinstance(brick_sound, Sound):
            brick_sound.set_volume(vol)
        if isinstance(lose_life_sound, Sound):
            lose_life_sound.set_volume(vol)
        if isinstance(coin_sound, Sound):
            coin_sound.set_volume(vol)
        if isinstance(blast_shoot_sound, Sound):
            blast_shoot_sound.set_volume(vol)
        if isinstance(pause_sound, Sound):
            pause_sound.set_volume(vol)
        if isinstance(unpause_sound, Sound):
            unpause_sound.set_volume(vol)
    except:
        pass

# --- Assets ---
def load_assets():
    """Load images, sounds, and apply initial volume."""
    global wall_sound, paddle_sound, brick_sound, lose_life_sound
    global coin_sound, blast_shoot_sound, pause_sound, unpause_sound
    global paddle_image, background

    vol = current_volume()  # always read volume fresh from config

    try:
        # Brick + wall + paddle impacts
        wall_sound = pygame.mixer.Sound(
            os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_wall-hit.wav')
        )
        wall_sound.set_volume(vol)

        paddle_sound = pygame.mixer.Sound(
            os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_paddle-hit.wav')
        )
        paddle_sound.set_volume(vol)

        brick_sound = pygame.mixer.Sound(
            os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_brick-hit.ogg')
        )
        brick_sound.set_volume(vol)

        lose_life_sound = pygame.mixer.Sound(
            os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_lose-lives.wav')
        )
        lose_life_sound.set_volume(vol)

        # Coin + blast
        coin_sound = Sound(
            os.path.join(ROOT_PATH, "media", "audio", "media_audio_collect_coin.ogg")
        )
        coin_sound.set_volume(vol)

        blast_shoot_sound = pygame.mixer.Sound(
            os.path.join(ROOT_PATH, 'media', 'audio', 'media_audio_blast_shoot.wav')
        )
        blast_shoot_sound.set_volume(vol)

        # Pause sound effects
        pause_sound = pygame.mixer.Sound(
            os.path.join(ROOT_PATH, "media", "audio", "pause.wav")
        )
        pause_sound.set_volume(vol)

        unpause_sound = pygame.mixer.Sound(
            os.path.join(ROOT_PATH, "media", "audio", "unpause.wav")
        )
        unpause_sound.set_volume(vol)

    except FileNotFoundError:
        print("Warning: Could not load one or more audio files.")

    # Load paddle sprite
    try:
        paddle_image = pygame.image.load(
            os.path.join(ROOT_PATH, 'media', 'graphics', 'paddle', 'paddle.png')
        ).convert_alpha()
        paddle_image = pygame.transform.scale(paddle_image, (BAR_WIDTH, BAR_HEIGHT))
    except FileNotFoundError:
        print("Warning: Could not load paddle image")
        paddle_image = pygame.Surface((BAR_WIDTH, BAR_HEIGHT))
        paddle_image.fill((255, 255, 255))

    # Load background image
    try:
        background = pygame.image.load(
            os.path.join(ROOT_PATH, 'media', 'graphics', 'background', 'back-black-wall-border.png')
        )
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except FileNotFoundError:
        background = None
        print("Warning: Could not load background. Using plain black.")

    apply_sound_volumes()


# ================= Game Flow =================

# --- Public Entry Point ---
def play(screen, debug_mode="", character_image=None):
    """External entry from main menu → begin a game session."""
    return main_controller(screen, debug_mode, character_image)


# --- Main Controller ---
def main_controller(screen, debug_mode="", character_image=None):
    """Handles level flow, debug modes, transitions, and win/lose state."""
    global tutorial_active, tutorial_timer, tutorial_phase, cfg, game_timer, level_timer
    global paddle_state, paddle_state_timer

    init(character_image)

    # ---- Mouse visibility based on config ----
    mouse_on = cfg.get("mouse_enabled", False)
    pygame.mouse.set_visible(mouse_on)

    tutorial_timer = 0
    tutorial_phase = "move"

    # Always reload config fresh at start of game
    with open(config_path, "r") as f:
        cfg = json.load(f)

    tutorial_active = cfg.get("tutorial_enabled", True)

    # Default level
    level = 1

    # Debug level overrides
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

    # FPS toggle: on for debug or if enabled in settings
    global show_fps
    show_fps = debug_mode is not False or cfg.get("show_fps", False)

    global debug_countdown_mode

    # --- "One Block" debug mode ---
    if debug_mode == "one_block":
        level = 0
        max_levels = 0
        scoreboard.lives = 1
        debug_countdown_mode = False

    # --- Countdown debug mode ---
    elif debug_mode == "countdown":
        level = 0
        max_levels = 0
        scoreboard.lives = 1
        debug_countdown_mode = True
        level_timer = Timer(screen, mode="countdown", countdown_time=10)
        pygame.display.set_caption("Breakout Game [COUNTDOWN]")

    # --- Timer setup based on level definition ---
    settings = get_level_settings(level)

    # Stopwatch timer always starts new game
    game_timer = Timer(screen, mode="stopwatch")

    # Boss/level-specific countdown timers
    if settings["timer"] == "countdown":
        level_timer = Timer(screen, mode="countdown", countdown_time=settings.get("time_limit", 60))
    else:
        level_timer = None

    # Override countdown for debug mode
    if debug_mode == "countdown":
        pygame.display.set_caption("Breakout Game [COUNTDOWN]")
        level_timer = Timer(screen, mode="countdown", countdown_time=10)
        level = 0
        max_levels = 0

    # Generate blocks
    blocks = define_blocks(screen, level)
    draw_bricks(screen, blocks)

    # Active effects
    particles = []
    coins = []
    powerups = []
    blasts = []

    # Apply tutorial state unless in debug
    if debug_mode:
        tutorial_active = False
    else:
        tutorial_active = cfg.get("tutorial_enabled", True)

    tutorial_timer = 0
    tutorial_phase = "move"

    # Reset powerup effects for new game
    global blast_active, blast_timer, paddle_state, paddle_state_timer
    blast_active = False
    blast_timer = 0
    paddle_state = "normal"
    paddle_state_timer = 0

    running = True
    while running:
        # Game loop returns status such as "running", "level_complete", etc.
        status = game_loop(
            screen, scoreboard, game_timer,
            blocks, debug_mode, level,
            particles, coins, powerups, blasts,
            blast_duration, cfg
        )

        if status == "running":
            continue

        if status == "quit":
            running = False

        elif status == "game_over":
            running = False

        elif status == "level_complete":
            # Stop boss music only when exiting level 5
            from common import boss_music, gameplay_music
            if level == 5:
                boss_music.stop()

            # Debug one-block mode → instant win
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

                # Past final level → win
                if level > max_levels:
                    if isinstance(game_timer, Timer):
                        game_timer.pause()
                    if isinstance(level_timer, Timer):
                        level_timer.pause()
                    set_win(True)
                    running = False
                else:
                    # Prepare next level
                    reset_all_effects(blasts, coins, powerups, particles)

                    blocks = define_blocks(screen, level)

                    # Configure new level timer
                    settings = get_level_settings(level)
                    if settings["timer"] == "countdown":
                        level_timer = Timer(screen, mode="countdown", countdown_time=settings.get("time_limit", 60))
                    else:
                        level_timer = None

                    # Level 5 → boss intro + boss music
                    if level == 5:
                        show_boss_intro(screen)

                        from common import menu_music, gameplay_music, boss_music, apply_music_volume
                        gameplay_music.stop()
                        menu_music.stop()
                        boss_music.play(loops=-1)
                        apply_music_volume(cfg.get("music_volume", 5))

    # After loop ends → show win/lose screen
    replay = False
    if win is not None:
        replay, initials = end_screen(screen, win, scoreboard.score)
        scoreboard.save_high_score(initials=initials, current_time=game_timer.get_time())

    return replay


# ================= Core Game Loop =================

def game_loop(screen, scoreboard, game_timer_ref, blocks, debug_mode, level,
              particles, coins, powerups, blasts, blast_duration, cfg):
    """Main per-frame loop: handles physics, drawing, timers, drops, input."""
    global ball_position, pause_requested, delta_time, blast_active, blast_timer
    global level_timer, ball_image
    global paddle_state, paddle_state_timer

    show_fps = (debug_mode is not False) or cfg.get("show_fps", False)

    # Draw environment
    walls = draw_wall(screen)
    bar = draw_bar(screen)
    draw_level(screen, level)

    # Draw all active balls
    for b in balls:
        # Use character skin if provided
        if ball_image:
            screen.blit(ball_image, (int(b["pos"].x) - ball_radius,
                                     int(b["pos"].y) - ball_radius))
        else:
            pygame.draw.circle(screen, WHITE,
                               (int(b["pos"].x), int(b["pos"].y)),
                               ball_radius)

    scoreboard.draw()

    # ---------- TIMER DISPLAY ----------
    if isinstance(level_timer, Timer):
        level_timer.draw()
    elif isinstance(game_timer_ref, Timer):
        game_timer_ref.draw()

    # If first ball not launched yet → reset positions each frame
    if not balls:
        reset_all_effects(blasts, coins, powerups, particles)

    # Input: returns False if user quits
    if not handle_input(bar, balls[0]):
        return "quit"

    # Draw all bricks
    draw_bricks(screen, blocks)

    # Apply collisions → score gain
    scoreboard.score += detect_collision(blocks, particles, coins, powerups, scoreboard)

    # ---------- Tutorial Logic ----------
    global tutorial_active, tutorial_timer, tutorial_phase

    if tutorial_active:
        tutorial_timer += delta_time

        # Cycle through tutorial phases based on time
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
            tutorial_active = False  # hide tutorial

    # ---------- PARTICLES ----------
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.is_dead():
            particles.remove(particle)

    # ---------- COINS ----------
    for coin in coins[:]:
        coin.update()
        coin.draw(screen)
        if coin.is_off_screen():
            coins.remove(coin)

    # Detect paddle → coin collection
    for coin in coins[:]:
        if coin.rect.bottom >= bar.top and coin.rect.colliderect(bar):
            scoreboard.add_points(50)
            coins.remove(coin)
            if isinstance(coin_sound, Sound):
                coin_sound.play()

    # ---------- POWERUPS ----------
    for powerup in powerups[:]:
        powerup.update()
        powerup.draw(screen)
        if powerup.is_off_screen():
            powerups.remove(powerup)

    # Paddle collects a falling powerup
    for powerup in powerups[:]:
        if bar.colliderect(powerup.rect):
            powerups.remove(powerup)

            # Activate effect based on type
            if powerup.type == "blast":
                blast_active = True
                blast_timer = blast_duration
            elif powerup.type == "small_paddle":
                paddle_state = "small"
                paddle_state_timer = paddle_power_duration
            elif powerup.type == "triple_ball":
                spawn_triple_ball()
            elif powerup.type == "big_paddle":
                paddle_state = "big"
                paddle_state_timer = paddle_power_duration

            if coin_sound:
                coin_sound.play()

    # ---------- BLAST AUTO-FIRE ----------
    if blast_active and blast_timer > 0:
        blast_timer -= 1

        # Fire alternating blasts every 10 frames
        if blast_timer % 10 == 0:
            if blast_timer % 20 == 0:
                blasts.append(BlueBlast(bar.left + 2, bar.top - 20))   # left shot
            else:
                blasts.append(BlueBlast(bar.right - 22, bar.top - 20))  # right shot

            if isinstance(blast_shoot_sound, Sound):
                blast_shoot_sound.play()

        # Disable blast when timer expires
        if blast_timer <= 0:
            blast_active = False

    # ---------- PADDLE SIZE TIMER ----------
    if paddle_state != "normal":
        paddle_state_timer -= 1
        if paddle_state_timer <= 0:
            paddle_state = "normal"

    # ---------- BLAST PROJECTILES ----------
    for blast in blasts[:]:
        blast.update()
        blast.draw(screen)
        if blast.is_off_screen():
            blasts.remove(blast)

    # Blasts hitting bricks
    for blast in blasts[:]:
        for block in blocks:
            if block.rect.colliderect(blast.rect):
                destroyed = block.hit()

                if destroyed:
                    # Brick breaks → particles + drop roll
                    for _ in range(15):
                        particles.append(Particle(block.rect.centerx,
                                                  block.rect.centery,
                                                  block.color))

                    drop = choose_drop()

                    if drop == "coin":
                        coins.append(Coin(block.rect.centerx - 15, block.rect.centery))
                    elif drop == "blast":
                        powerups.append(PowerUp(block.rect.centerx - 15,
                                                block.rect.centery, "blast"))
                    elif drop == "triple_ball":
                        powerups.append(PowerUp(block.rect.centerx - 15,
                                                block.rect.centery, "triple_ball"))
                    elif drop == "small_paddle":
                        powerups.append(PowerUp(block.rect.centerx - 15,
                                                block.rect.centery, "small_paddle"))
                    elif drop == "big_paddle":
                        powerups.append(PowerUp(block.rect.centerx - 15,
                                                block.rect.centery, "big_paddle"))

                    blocks.remove(block)
                    scoreboard.add_points(50)

                    if isinstance(brick_sound, Sound):
                        brick_sound.play()

                blasts.remove(blast)
                break  # stop checking other blocks for this blast

    # ---------- LEVEL COMPLETE ----------
    if len(blocks) == 0:
        if isinstance(game_timer, Timer):
            game_timer.pause()
        if isinstance(level_timer, Timer):
            level_timer.pause()
        return "level_complete"

    # ---------- BALL MOVEMENT ----------
    if not move_ball(screen, walls, bar, balls):
        # Ball lost → update scoreboard & life handling
        if not update_scoreboard(screen, scoreboard, game_timer_ref, blasts, coins, powerups, particles):
            return "game_over"

    # ---------- COUNTDOWN TIMER END ----------
    if level_timer and level_timer.get_time() <= 0:
        if isinstance(level_timer, Timer):
            level_timer.pause()
        if isinstance(game_timer, Timer):
            game_timer.pause()

        set_win(False)
        return "game_over"

    # ---------- PAUSE ----------
    if pause_requested:
        if isinstance(game_timer, Timer):
            game_timer.pause()
        if isinstance(level_timer, Timer):
            level_timer.pause()

        paused = pause_game(screen)
        pause_requested = False

        if not paused:
            return "quit"

        # Resume timers after unpausing
        if isinstance(game_timer, Timer):
            game_timer.resume()
        if isinstance(level_timer, Timer):
            level_timer.resume()

    # ---------- TIMER UPDATES ----------
    if isinstance(game_timer, Timer):
        game_timer.update()
    if isinstance(level_timer, Timer):
        level_timer.update()

    # ---------- FPS DISPLAY ----------
    if show_fps:
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 0))
        fps_rect = fps_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        screen.blit(fps_text, fps_rect)

    pygame.display.flip()

    delta_time = clock.tick(60)
    return "running"


def define_blocks(screen, level, wall_padding=WALL_PADDING):
    """Define the brick layout for the current level."""
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


def handle_input(bar, main_ball):
    """Keyboard + mouse handling, launch logic, paddle movement."""
    global pause_requested, bar_x, tutorial_active

    mouse_enabled = cfg.get("mouse_enabled", False)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # ---------- KEYBOARD ----------
        if event.type == pygame.KEYDOWN:

            # Pause
            if event.key == pygame.K_ESCAPE:
                if isinstance(pause_sound, Sound):
                    pause_sound.set_volume(current_volume())
                    pause_sound.play()
                pause_requested = True
                return True

            # Tutorial: SPACE ends tutorial and launches
            if tutorial_active and event.key == pygame.K_SPACE:
                tutorial_active = False

                balls[0]["vel"].x = get_x_angle(bar, balls[0])
                balls[0]["vel"].y = -5

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

            # Normal launch
            if event.key == pygame.K_SPACE and main_ball["vel"].length() == 0 and not tutorial_active:
                bar_center = bar.centerx
                ball_center = main_ball["pos"].x

                # Center correction
                if abs(ball_center - bar_center) < 3:
                    main_ball["pos"].x = bar_center

                main_ball["vel"].x = get_x_angle(bar, main_ball)
                if abs(main_ball["vel"].x) < 0.5:
                    main_ball["vel"].x = 0

                main_ball["vel"].y = -6

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

        # ---------- MOUSE CLICK LAUNCH ----------
        if mouse_enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Tutorial click launch
            if tutorial_active:
                tutorial_active = False

                balls[0]["vel"].x = get_x_angle(bar, balls[0])
                balls[0]["vel"].y = -5

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

            # Normal mouse launch
            if main_ball["vel"].length() == 0:
                bar_center = bar.centerx
                ball_center = main_ball["pos"].x

                if abs(ball_center - bar_center) < 3:
                    main_ball["pos"].x = bar_center

                main_ball["vel"].x = get_x_angle(bar, main_ball)
                if abs(main_ball["vel"].x) < 0.5:
                    main_ball["vel"].x = 0

                main_ball["vel"].y = -6

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

    # ---------- PADDLE MOVEMENT ----------
    keys = pygame.key.get_pressed()
    paddle_width = int(getattr(draw_bar, "width", BAR_WIDTH))

    # Movement BEFORE launch
    if main_ball["vel"].length() == 0:
        ball_x = main_ball["pos"].x
        left_limit = int(ball_x - (paddle_width - ball_radius * 2))
        right_limit = int(ball_x - ball_radius * 2)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            bar_x = max(bar_x - speed, left_limit)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            bar_x = min(bar_x + speed, right_limit)

    else:
        # Movement AFTER launch
        edge_adjust = 8
        current_width = int(getattr(draw_bar, "width", BAR_WIDTH))

        min_x = WALL_PADDING - edge_adjust
        max_x = SCREEN_WIDTH - WALL_PADDING - current_width + edge_adjust

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            bar_x = max(bar_x - speed, min_x)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            bar_x = min(bar_x + speed, max_x)

    # ---------- MOUSE MOVEMENT ----------
    if mouse_enabled:
        mx = pygame.mouse.get_pos()[0]
        target_x = mx - (paddle_width // 2)

        current_width = int(getattr(draw_bar, "width", BAR_WIDTH))

        # Pre-launch limits
        if main_ball["vel"].length() == 0:
            ball_x = main_ball["pos"].x
            left_limit = int(ball_x - (paddle_width - ball_radius * 2))
            right_limit = int(ball_x - ball_radius * 2)
            target_x = max(left_limit, min(target_x, right_limit))
        else:
            # Wall limits
            target_x = max(
                WALL_PADDING,
                min(target_x, SCREEN_WIDTH - WALL_PADDING - current_width)
            )

        # Smooth mouse movement
        screen_distance = (SCREEN_WIDTH - WALL_PADDING * 2 - paddle_width)
        frames_needed = 120
        max_step = screen_distance / frames_needed

        if bar_x < target_x:
            bar_x = min(bar_x + max_step, target_x)
        elif bar_x > target_x:
            bar_x = max(bar_x - max_step, target_x)

    return True


# ================= Movement & Physics =================
# Handles ball movement, wall bouncing, and paddle collisions.
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
        steps = 3
        for _ in range(steps):
            b["pos"] += b["vel"] / steps

        wall_check_multi(b, walls)
        paddle_check_multi(b, bar)

        if b["pos"].y - ball_radius > SCREEN_HEIGHT:
            balls_list.remove(b)

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

    if hit_wall and isinstance(wall_sound, Sound):
        wall_sound.play()


# ---------- Paddle Collision ----------
def paddle_check_multi(ball, bar):
    global last_hit_ball

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

        last_hit_ball = ball


def get_x_angle(bar, ball_dict):
    ball_center_x = ball_dict["pos"].x
    bar_center_x = bar.centerx
    offset = ball_center_x - bar_center_x
    ratio = ball_max_velocity_x / (bar.width / 2)
    return offset * ratio


# ================= Collision & Drops =================
def detect_collision(blocks, particles, coins, powerups, scoreboard):
    global balls, blast_active

    score_increase = 0

    for ball in balls[:]:
        ball_rect = pygame.Rect(
            ball["pos"].x - ball_radius,
            ball["pos"].y - ball_radius,
            ball_radius*2,
            ball_radius*2
        )
        block_index = ball_rect.collidelist(blocks)

        if block_index != -1:
            block = blocks[block_index]

            # ---- COLLISION ANGLE CALCULATION ----
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

            destroyed = block.hit()

            if destroyed:
                for _ in range(15):
                    particles.append(
                        Particle(block.rect.centerx, block.rect.centery, block.color)
                    )

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
    global balls, last_hit_ball

    if len(balls) == 0:
        return

    if last_hit_ball in balls:
        base = last_hit_ball
    else:
        base = balls[0]

    new_velocity = abs(base["vel"].x or 3)

    left_pos = base["pos"].copy()
    right_pos = base["pos"].copy()

    left_pos.x -= 25
    right_pos.x += 25

    balls.append({"pos": left_pos,
                  "vel": pygame.Vector2(-new_velocity, -5)})
    balls.append({"pos": right_pos,
                  "vel": pygame.Vector2(new_velocity, -5)})


# ================= UI & Drawing =================
# Draws wall, paddle, bricks, level text, tutorial prompts, and level transitions.

# ---------- Wall ----------
def draw_wall(screen):
    # Background image or solid black
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BLACK)

    wall_bottom = SCREEN_HEIGHT - 150

    # Wall rect controls ball boundaries
    return pygame.Rect(
        WALL_PADDING,
        WALL_TOP_PADDING,
        SCREEN_WIDTH - WALL_PADDING * 2,
        wall_bottom - WALL_TOP_PADDING
    )


# ---------- Draw Paddle ----------
def draw_bar(screen):
    global bar_x, paddle_state

    # Pick target size based on power-up
    if paddle_state == "small":
        target_width = small_paddle_width
    elif paddle_state == "big":
        target_width = big_paddle_width
    else:
        target_width = original_paddle_width

    # Smooth width transition
    current_width = getattr(draw_bar, "width", original_paddle_width)
    current_width += (target_width - current_width) * 0.10
    draw_bar.width = current_width

    # Keep paddle centered when width changes
    old_width = getattr(draw_bar, "stored_width", original_paddle_width)
    width_change = current_width - old_width
    bar_x -= width_change / 2
    draw_bar.stored_width = current_width

    bar = pygame.Rect(bar_x, bar_y, current_width, BAR_HEIGHT)
    image_y_offset = -11

    # Color-tint paddle during size power-ups
    state = paddle_state

    if paddle_state in ("small", "big") and paddle_image:
        tinted = paddle_image.copy()
        tinted.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
        if paddle_state == "small":
            tinted.fill((255, 40, 40), special_flags=pygame.BLEND_RGB_ADD)
        else:
            tinted.fill((40, 140, 255), special_flags=pygame.BLEND_RGB_ADD)
        current_img = tinted
    else:
        current_img = paddle_image

    # Draw paddle image or fallback rectangle
    if current_img:
        scaled_paddle = pygame.transform.scale(current_img, (int(current_width), BAR_HEIGHT))
        screen.blit(scaled_paddle, (bar_x, bar_y + image_y_offset))
    else:
        pygame.draw.rect(screen, RED, bar)

    return bar


# ---------- Block Drawing ----------
def draw_bricks(screen, blocks):
    # Draw each brick with image if available
    for block in blocks:
        if block.image is not None:
            screen.blit(block.image, block.rect)
        else:
            pygame.draw.rect(screen, block.color, block.rect)


def draw_level(screen, level):
    # Displays current level at top of the screen
    text = font.render(f"LEVEL {level}", True, (255, 255, 0))
    rect = text.get_rect(center=(SCREEN_WIDTH // 2, WALL_TOP_PADDING - 40))
    screen.blit(text, rect)


# ---------- Tutorial Phase ----------
def show_tutorial_phase(screen, phase):
    tutorial_path = os.path.join(ROOT_PATH, "media", "graphics", "tutorial")

    # Load icons used in tutorial prompts
    arrow_img = pygame.image.load(os.path.join(tutorial_path, "arrow_keys.png"))
    wasd_img = pygame.image.load(os.path.join(tutorial_path, "wasd_keys.png"))
    esc_img = pygame.image.load(os.path.join(tutorial_path, "Esc Key.png"))
    space_img = pygame.image.load(os.path.join(tutorial_path, "Space Bar.png"))

    arrow_img = pygame.transform.scale(arrow_img, (140, 140))
    wasd_img = pygame.transform.scale(wasd_img, (140, 140))
    esc_img = pygame.transform.scale(esc_img, (140, 140))
    space_img = pygame.transform.scale(space_img, (260, 80))

    font = pygame.font.Font(pixel_font_path, 42)
    label_font = pygame.font.Font(pixel_font_path, 28)

    # Movement tutorial
    if phase == "move":
        arrow_pos = (SCREEN_WIDTH // 2 - 180, 290)
        wasd_pos = (SCREEN_WIDTH // 2 + 40, 290)

        screen.blit(arrow_img, arrow_pos)
        screen.blit(wasd_img, wasd_pos)

        text = font.render("Use ARROW KEYS or A/D to move", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 460))

    # Pause tutorial
    if phase == "pause":
        esc_pos = (SCREEN_WIDTH // 2 - 70, 290)
        screen.blit(esc_img, esc_pos)

        text = font.render("Press ESC to pause the game", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 460))

    # Launch tutorial
    if phase == "launch":
        space_pos = (SCREEN_WIDTH // 2 - 130, 320)
        screen.blit(space_img, space_pos)

        text = font.render("Press SPACE to launch the ball", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 460))


def show_level_complete(screen, level):
    # Simple level-completed splash text
    message = font.render(f"LEVEL {level} COMPLETE!", True, (255, 255, 0))
    message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(message, message_rect)
    pygame.display.flip()
    pygame.time.wait(1000)


def show_boss_intro(screen):
    big_font = pygame.font.Font(pixel_font_path, 76)
    small_font = pygame.font.Font(pixel_font_path, 36)

    lines = [
        "FINAL LEVEL!",
        "THE BOSS AWAITS.",
        "You have 1 minute to destroy all bricks.",
        "Press SPACE to begin..."
    ]

    screen.fill((0, 0, 0))

    # Print each intro line spaced vertically
    y = SCREEN_HEIGHT // 2 - 120
    for i, text in enumerate(lines):
        font = big_font if i == 0 else small_font
        surf = font.render(text, True, (255, 255, 255))
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(surf, rect)
        y += 70

    pygame.display.flip()

    # Wait until SPACE to continue
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False


# ================= Game State =================
# Life loss, respawn, and game over handling.

# ---------- Reset All Effects ----------
def reset_all_effects(blasts, coins, powerups, particles):
    """Master reset: ball, paddle, power-ups, and falling items."""
    global balls, bar_x
    global blast_active, blast_timer
    global paddle_state, paddle_state_timer
    global last_hit_ball

    # Reset all effect states
    blast_active = False
    blast_timer = 0
    paddle_state = "normal"
    paddle_state_timer = 0
    last_hit_ball = None

    # Reset paddle visuals
    draw_bar.width = original_paddle_width
    draw_bar.stored_width = original_paddle_width

    # Reset paddle position
    bar_x = (SCREEN_WIDTH - original_paddle_width) // 2

    # Reset ball list
    balls = [
        {
            "pos": pygame.Vector2(SCREEN_WIDTH // 2, bar_y - ball_radius - 4),
            "vel": pygame.Vector2(0, 0)
        }
    ]

    # Clear falling objects
    blasts.clear()
    coins.clear()
    powerups.clear()
    particles.clear()


def update_scoreboard(screen, scoreboard, timer, blasts, coins, powerups, particles):
    global ball_position, ball_velocity, bar_x
    global blast_active, blast_timer
    global paddle_state, paddle_state_timer

    # Player loses one life
    scoreboard.lose_life()
    if isinstance(lose_life_sound, Sound):
        lose_life_sound.play()

    # Pause timers during life reset
    if isinstance(game_timer, Timer):
        game_timer.pause()
    if isinstance(level_timer, Timer):
        level_timer.pause()

    # If player still has lives, reset ball and paddle
    if scoreboard.lives > 0:
        global last_hit_ball
        last_hit_ball = None

        reset_all_effects(blasts, coins, powerups, particles)

        message = font.render(f"Lives Left: {scoreboard.lives}", True, WHITE)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(1000)
        return True

    # No lives left → game over
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
    # Update timers for clean pause display
    if isinstance(game_timer, Timer):
        game_timer.update()
    if isinstance(level_timer, Timer):
        level_timer.update()

    snapshot = screen.copy()
    choice = pause_overlay(snapshot)
    if choice == "menu":
        pygame.mouse.set_visible(True)
        return False

    if choice == "resume":
        if isinstance(unpause_sound, Sound):
            unpause_sound.set_volume(current_volume())
            unpause_sound.play()
        return True