import random
import sys
import pygame
import common

from objects.pipe import Pipe
from common import BLACK, WHITE, RED, BLUE

clock = pygame.time.Clock()
delta_time = 1
screen_width, screen_height = common.screen_width, common.screen_height
level = 1
alive = True
score = 0

# Set up the initial position and speed of the player
player_height = 20
player_width = 40
player_speed_max = 7
player_speed = 7
player_position = pygame.Vector2(float(80), float((screen_height - player_height) // 2))
jump_strength = 100
jump_position = None

def main_controller(screen):
    global delta_time
    global jump_position
    global player_position
    global player_speed
    global alive
    global score
    pygame.display.set_caption("Flappy Like Game")
    font = pygame.font.SysFont(None, 48)  # Default font, size 48

    obstacles = create_obstacles()

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    jump_position = pygame.Vector2(player_position.x, float(player_position.y - jump_strength))


        text_surface = font.render(f"Score: {score}", True, WHITE)

        if jump_position is not None:
            if player_position.y <= jump_position.y + 20:
                jump_position = None
                player_speed = pygame.math.lerp(0, player_speed_max, 0.6)
            else:
                player_position = player_position.lerp(jump_position, 0.1)
        else:
            player_speed = pygame.math.lerp(0, player_speed_max, 0.5)
            player_position.y += player_speed

        if player_position.y + player_height > screen_height:
            player_position.y = screen_height - player_height
        elif player_position.y < 0:
            player_position.y = 1
            jump_position = None

        # Fill the screen with black color
        screen.fill(BLACK)

        # Draw the red square
        player = pygame.draw.rect(screen, RED, (player_position.x, player_position.y, player_width, player_height))

        for obstacle in obstacles:
            obstacle.position.x -= delta_time * obstacle.speed
            if obstacle.position.x < 0 - obstacle.width:
                obstacles.remove(obstacle)
                score += 1
            o = pygame.draw.rect(screen, BLUE, (obstacle.position.x, obstacle.position.y, obstacle.width, obstacle.height))
            if o.colliderect(player):
                alive = False

        # Placeholder death action
        if not alive:
            pygame.quit()
            sys.exit()

        screen.blit(text_surface, (10, 10))
        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        delta_time = clock.tick(60)

    # Quit Pygame
    pygame.quit()
    sys.exit()


def create_obstacles():
    obstacles = []
    num_obstacles = 100
    block_space = (170, 220)

    column = 0
    for i in range(num_obstacles):
        obstacles.append(Pipe(pygame.Vector2(screen_width + (random.randint(block_space[0], block_space[1]) * i), random.randint(0, screen_height)), 0.5))
        column += 1

    return obstacles

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    main_controller(pygame.display.set_mode((common.screen_width, common.screen_height)))