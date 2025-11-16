import pygame
import random

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 6)
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-5, -2)
        self.gravity = 0.3
        self.lifetime = 30  # frames
        self.age = 0
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
        self.age += 1
        self.size = max(1, self.size - 0.1)  # shrink over time
        
    def draw(self, screen):
        if self.age < self.lifetime:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))
            
    def is_dead(self):
        return self.age >= self.lifetime or self.size <= 1