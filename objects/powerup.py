import pygame
import os
from common import ROOT_PATH, SCREEN_HEIGHT

class PowerUp:
    def __init__(self, x, y, powerup_type="blast"):
        self.width = 30
        self.height = 30
        self.x = x
        self.y = y
        self.velocity_y = 5
        self.type = powerup_type  # "blast" or "small_paddle"
        
        # Load power-up image based on type
        self.image = None
        try:
            if powerup_type == "blast":
                img = pygame.image.load(os.path.join(ROOT_PATH, "media", "graphics", "Particles", "blast.png"))
            elif powerup_type == "small_paddle":
                img = pygame.image.load(os.path.join(ROOT_PATH, "media", "graphics", "Particles", "small paddle.png"))
            self.image = pygame.transform.scale(img, (self.width, self.height))
        except Exception as e:
            print(f"Warning: Could not load {powerup_type} image - {e}")
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self):
        self.y += self.velocity_y
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (0, 100, 255), (self.x, self.y, self.width, self.height))
        
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT


class BlueBlast:
    def __init__(self, x, y):
        self.width = 20
        self.height = 40
        self.x = x
        self.y = y
        self.velocity_y = -8
        
        self.image = None
        try:
            img = pygame.image.load(os.path.join(ROOT_PATH, "media", "graphics", "Particles", "blue-blast.png"))
            self.image = pygame.transform.scale(img, (self.width, self.height))
        except Exception as e:
            print(f"Warning: Could not load blue-blast.png - {e}")
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self):
        self.y += self.velocity_y
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (0, 150, 255), (self.x, self.y, self.width, self.height))
        
    def is_off_screen(self):
        return self.y < 120