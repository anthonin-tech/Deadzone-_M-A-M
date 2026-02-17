import pygame
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

class Projectile(pygame.sprite.Sprite):
        def __init__(self, x, y, direction, speed=700, damage=10, radius=4, color=(255, 230, 120), max_distance=900):
                super().__init__()
                self.position = pygame.Vector2(x, y)
                self.direction = pygame.Vector2(direction)

                if self.direction.length_squared() == 0:
                        self.direction = pygame.Vector2(1, 0)
                else:
                        self.direction = self.direction.normalize()
                
                self.speed = speed
                self.damage = damage
                self.radius = radius
                self.color = color
                self.max_distance = max_distance
                self.distance_travelled = 0
                self.alive = True

        def update(self, dt):
                if not self.alive:
                        return
                
                movement = self.direction * self.speed * dt
                self.position += movement
                self.distance_travelled += movement.length()

                if self.distance_travelled >= self.max_distance:
                        self.alive = False
        
        def draw(self, screen):
                if self.alive:
                        pygame.draw.circle(
                                screen, 
                                (255, 230, 120), 
                                (int(self.position.x), 
                                int(self.position.y)),
                                self.radius
                                )

