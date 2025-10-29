import sys
import pygame
import common

def show_instructions(screen):
    """Simple instruction screen"""
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)
    screen_width = screen.get_width()

    # Display the list of controls and instructions
    instructions = [
        "Use the SPACE bar to launch the ball on a new life.",
        "Use the arrow keys or A/D to move the paddle.",
        "Bounce the ball to break all the blocks.",
        "You have 3 lives. The game ends when they run out.",
        "Press ESC to go back to the menu."
    ]

    waiting = True
    while waiting:
        # Fill background with gradient for consistency
        common.draw_gradient_background(screen, (10, 10, 50), (0, 0, 0))

        # Draw the "How to Play" title
        title = font.render("How to Play", True, common.WHITE)
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 120))

        # Draw each instruction line
        y = 220
        for line in instructions:
            text = small_font.render(line, True, common.WHITE)
            screen.blit(text, (screen_width // 2 - text.get_width() // 2, y))
            y += 50

        # Return message
        back_text = small_font.render("Press ESC to return", True, common.RED)
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
