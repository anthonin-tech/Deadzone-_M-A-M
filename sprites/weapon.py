import pygame
import random
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from sprites.projectile import Projectile

class Weapon:
    PROFILES = {
        "pistol": {
            "cooldown_ms": 320,
            "projectile_speed": 700,
            "projectile_damage": 12,
            "pellets": 1,
            "spread_deg": 1.5,
            "max_distance": 380
        },
        "shotgun": {
            "cooldown_ms": 900,
            "projectile_speed": 540,
            "projectile_damage": 7,
            "pellets": 8,
            "spread_deg": 18,
            "max_distance": 175
        },
    }

    def __init__(self, profile_name):
        data = self.PROFILES[profile_name]
        self.profile_name = profile_name
        self.cooldown_ms = data["cooldown_ms"]
        self.projectile_speed = data["projectile_speed"]
        self.projectile_damage = data["projectile_damage"]
        self.pellets = data["pellets"]
        self.spread_deg = data["spread_deg"]
        self.max_distance = data["max_distance"]
    
    @classmethod
    def from_item(cls, item):
        name = item.name.lower()
        if "pompe" in name :
            return cls("shotgun")
        if "pistolet" in name:
            return cls("pistol")
        return cls("pistol")
    
    def shoot(self, origin, target):
        direction = pygame.Vector2(target) - pygame.Vector2(origin)
        if direction.length_squared() == 0:
            return []
        
        base_angle = math.atan2(direction.y, direction.x)
        projectiles = []

        for _ in range(self.pellets):
            offset = random.uniform(-self.spread_deg / 2, self.spread_deg / 2)
            angle = base_angle + math.radians(offset)
            shot_dir = pygame.Vector2(math.cos(angle), math.sin(angle))

            p = Projectile(
                origin.x,
                origin.y,
                shot_dir,
                speed=self.projectile_speed,
                damage=self.projectile_damage,
                radius=4,
                max_distance=self.max_distance,
                owner="player"
            )
            projectiles.append(p)
        
        return projectiles
