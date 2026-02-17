import pygame
import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

class Enemy():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 55
        self.radius = 10
        self.color = (255, 0, 0)

        self.health = 40
        self.max_health = 20

        self.detection_radius = 200
        self.attack_distance = 50
        self.damage = 10
        self.attack_cooldown = 1000
        self.last_attack = 0
        
    def calculate_distance(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        return math.sqrt(dx**2 + dy**2)
    
    def move_towards(self, target_x, target_y, dt):
        distance = self.calculate_distance(target_x, target_y)
        if distance > 0:
            dx = (target_x - self.x) /  distance
            dy = (target_y - self.y) / distance
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
        
    def can_attack(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_attack >= self.attack_cooldown
    
    def update(self, dt):
        pass

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 15)

    
     