import pygame
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from systems.inventory import Items
from systems.projectile import Projectile

class Weapon:
    def __init__(self, name, damage, cooldown, projectile_speed):
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.projectile_speed = projectile_speed

        self.last_shot_time = 0

    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot_time >= self.cooldown
    
    def shoot(self, position, direction):
        if not self.can_shoot():
            return None
        
        self.last_shot_time =pygame.time.get_ticks()

        projectile = Projectile(
            position=position,
            direction=direction,
            speed=self.projectile_speed,
            damage=self.damage
        )

        return projectile

        
