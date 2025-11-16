import pygame
import os
from common import ROOT_PATH, SCREEN_HEIGHT

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.velocity_y = 5  # Falling speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Load coin image
        try:
            self.image = pygame.image.load(os.path.join(ROOT_PATH, "media", "graphics", "Particles", "coin.png"))
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except:
            self.image = None
            print("Warning: Could not load coin.png")
        
    def update(self):
        self.y += self.velocity_y
        self.rect.y = self.y
        
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Fallback: draw gold circle if image fails
            pygame.draw.circle(screen, (255, 215, 0), (int(self.x + self.width//2), int(self.y + self.height//2)), self.width//2)
        
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT