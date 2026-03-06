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
            "attack_type": "ranged",
            "cooldown_ms": 320,
            "projectile_speed": 700,
            "projectile_damage": 12,
            "pellets": 1,
            "spread_deg": 1.5,
            "max_distance": 380
        },
        "shotgun": {
            "attack_type": "ranged",
            "cooldown_ms": 900,
            "projectile_speed": 540,
            "projectile_damage": 7,
            "pellets": 8,
            "spread_deg": 18,
            "max_distance": 175
        },
        "axe": {
            "cooldown_ms": 1000,
            "attack_type": "melee",
            "melee_damage": 26,
            "melee_range": 68,
            "melee_arc_deg": 150
        }
    }

    def __init__(self, profile_name):
        data = self.PROFILES[profile_name]
        self.profile_name = profile_name
        self.attack_type = data.get("attack_type", "ranged")
        self.cooldown_ms = data["cooldown_ms"]
        self.projectile_speed = data.get("projectile_speed", 0)
        self.projectile_damage = data.get("projectile_damage", 0)
        self.pellets = data.get("pellets", 0)
        self.spread_deg = data.get("spread_deg", 0)
        self.max_distance = data.get("max_distance", 0)
        self.melee_damage = data.get("melee_damage", 0)
        self.melee_range = data.get("melee_range", 0)
        self.melee_arc_deg = data.get("melee_arc_deg", 0)

    @classmethod
    def from_item(cls, item):
        name = item.name.lower()
        if "pompe" in name :
            return cls("shotgun")
        if "hache" in name or "axe" in name:
            return cls("axe")
        if "pistolet" in name:
            return cls("pistol")
        return cls("pistol")

    def shoot(self, origin, target):
        if self.attack_type == "melee":
            return []

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
