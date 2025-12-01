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


class ExplosionParticle:
    """Particle specifically for explosion effects with glow"""
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
    
    def create_explosion(self, x, y, color=(255, 200, 50), num_particles=50):
        """Create an explosion at x, y position"""
        # Main colored particles
        for _ in range(num_particles):
            self.particles.append(ExplosionParticle(x, y, color))
        
        # White-hot core particles
        for _ in range(20):
            self.particles.append(ExplosionParticle(x, y, (255, 255, 255)))
        
        # Orange outer particles
        for _ in range(15):
            self.particles.append(ExplosionParticle(x, y, (255, 150, 0)))
    
    def update(self):
        """Update all particles, remove dead ones"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)


class Fireball:
    """Single fireball that shoots toward a targeted brick"""
    def __init__(self, x, y, target_x, target_y, fireball_image=None):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 12
        self.active = True
        self.trail_particles = []
        
        # Load fireball image if not provided
        if fireball_image is None:
            try:
                import os
                from common import ROOT_PATH
                img = pygame.image.load(os.path.join(ROOT_PATH, "media", "graphics", "Particles", "moving_fireball.png"))
                self.fireball_image = pygame.transform.scale(img, (30, 30))
            except:
                self.fireball_image = None
        else:
            self.fireball_image = fireball_image
        
        # Calculate direction to target
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = 0
            self.vy = -self.speed
        
        self.radius = 15
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # Add trail particles
        if random.random() < 0.3:
            trail_color = random.choice([(255, 150, 0), (255, 200, 50), (255, 100, 0)])
            self.trail_particles.append(ExplosionParticle(self.x, self.y, trail_color))
        
        # Update trail
        self.trail_particles = [p for p in self.trail_particles if p.update()]
        
        # Deactivate if off screen
        if self.y < -50 or self.y > 800 or self.x < -50 or self.x > 750:
            self.active = False
    
    def draw(self, screen):
        # Draw trail
        for particle in self.trail_particles:
            particle.draw(screen)
        
        # Draw fireball image or circle
        if self.fireball_image:
            screen.blit(self.fireball_image, (int(self.x - 15), int(self.y - 15)))
        else:
            # Draw glowing fireball
            for i in range(3):
                glow_radius = self.radius + (10 - i * 3)
                alpha = 100 - (i * 30)
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                glow_color = (255, 150, 0, alpha)
                pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surf, (int(self.x - glow_radius), int(self.y - glow_radius)))
            
            # Core fireball
            pygame.draw.circle(screen, (255, 200, 50), (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (255, 255, 200), (int(self.x), int(self.y)), self.radius - 5)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)