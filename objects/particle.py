"""
This file creates the Particle object for the game.
It controls how each particle moves, shrinks, and disappears.
"""

import pygame
import random


# ---------- PARTICLE CLASS ---------- #
# Particle object used for small visual effects.
class Particle:
    # Setup the particle with position, color, and movement.
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 6)
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-5, -2)
        self.gravity = 0.3
        self.lifetime = 30
        self.age = 0

    # Update the particle movement and shrink it over time.
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
        self.age += 1
        self.size = max(1, self.size - 0.1)

    # Draw the particle on the screen.
    def draw(self, screen):
        if self.age < self.lifetime:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.x), int(self.y)),
                int(self.size)
            )

    # Check if the particle should be removed.
    def is_dead(self):
        return self.age >= self.lifetime or self.size <= 1