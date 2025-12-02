import pygame
import random
import math

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

# Particle specifically for explosion effects with glow
class ExplosionParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.size = random.randint(4, 10)
        self.life = random.randint(25, 45)
        self.max_life = self.life
        self.glow_size = random.randint(15, 30)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity
        self.life -= 1
        self.size = max(1, self.size - 0.15)
        return self.life > 0
    
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            
            # Draw glow effect (multiple layers for better glow)
            for i in range(3):
                glow_size = int(self.glow_size - (i * 5))
                if glow_size > 0:
                    glow_alpha = max(0, alpha // (i + 2))
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    glow_color = (*self.color, glow_alpha)
                    pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
                    screen.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))
            
            # Draw core particle
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))


class ExplosionManager:
    """Manages all explosion particle effects"""
    def __init__(self):
        self.particles = []
    
    def create_explosion(self, x, y, color=(255, 200, 50), num_particles=40):
        """Create an explosion at x, y position"""
        # Main colored particles (reduced from 50 to 20)
        for _ in range(num_particles):
            self.particles.append(ExplosionParticle(x, y, color))
        
        # White-hot core particles (reduced from 20 to 8)
        for _ in range(8):
            self.particles.append(ExplosionParticle(x, y, (255, 255, 255)))
        
        # Orange outer particles (reduced from 15 to 6)
        for _ in range(6):
            self.particles.append(ExplosionParticle(x, y, (255, 150, 0)))
    
    def update(self):
        """Update all particles, remove dead ones"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)


class Fireball:
    """Fireball projectile that shoots upward """
    def __init__(self, x, y):
        self.width = 30
        self.height = 30
        self.x = x
        self.y = y
        self.velocity_y = -10  
        self.trail_particles = []
        
        # Load fireball image
        self.image = None
        try:
            import os
            from common import ROOT_PATH
            img = pygame.image.load(os.path.join(ROOT_PATH, "media", "graphics", "Particles", "moving_fireball.png"))
            self.image = pygame.transform.scale(img, (self.width, self.height))
        except Exception as e:
            print(f"Warning: Could not load moving_fireball.png - {e}")
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active = True
        
    def update(self):
        self.y += self.velocity_y
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Add trail particles occasionally
        if random.random() < 0.4:
            trail_color = random.choice([(255, 150, 0), (255, 200, 50), (255, 100, 0)])
            self.trail_particles.append(ExplosionParticle(self.x + self.width//2, self.y + self.height//2, trail_color))
        
        # Update trail
        self.trail_particles = [p for p in self.trail_particles if p.update()]
        
        # Deactivate if off screen
        if self.y < -50:
            self.active = False
        
    def draw(self, screen):
        # Draw trail first (behind fireball)
        for particle in self.trail_particles:
            particle.draw(screen)
        
        # Draw fireball
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Fallback: draw orange/red circle with glow
            center_x = int(self.x + self.width // 2)
            center_y = int(self.y + self.height // 2)
            radius = self.width // 2
            
            # Glow effect
            for i in range(3):
                glow_radius = radius + (8 - i * 2)
                alpha = 80 - (i * 25)
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                glow_color = (255, 150, 0, alpha)
                pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius))
            
            # Core fireball
            pygame.draw.circle(screen, (255, 200, 50), (center_x, center_y), radius)
            pygame.draw.circle(screen, (255, 255, 200), (center_x, center_y), radius - 4)
            
    def is_off_screen(self):
        return self.y < 120  