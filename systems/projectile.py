import pygame
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

class Projectile:
    def __init__(self, position, direction, speed, damage):
        self.damage = damage
        self.position = pygame.Vector2(position)
        self.direction = pygame.Vector2(direction).normalize()
        self.speed = speed

        self.rect = pygame.Rect(
            self.position.x,
            self.position.y,
            6,
            6
        )

        self.alive = True

    def update(self):
        self.position += self.direction * self.speed
        self.rect.center = self.position

        if not pygame.display.get_surface().get_rect().colliderect(self.rect):
            self.alive = False

        