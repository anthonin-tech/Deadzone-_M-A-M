import time
import pygame
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from sprites.player import Player


class MAMPlayer(Player):
    SPRITE_COLUMN     = 0
    CHARACTER_NAME    = "MAM"
    POWER_NAME        = "Pouvoir"
    POWER_DESCRIPTION = ""

    DISPLAY_W = 16
    DISPLAY_H = 16

    def __init__(self, x=640, y=360):
        super().__init__(x=x, y=y)

        self.power_active    = False
        self.cooldown_active = False
        self._power_start    = 0.0
        self.POWER_DURATION  = 60.0
        self.POWER_COOLDOWN  = 60.0

        self._current_dir   = "down"
        self._sheet_loaded  = False
        self._try_load_sheet()

    def _try_load_sheet(self):
        base_dir   = os.path.dirname(os.path.abspath(__file__))
        sheet_path = os.path.join(base_dir, "..", "asset", "player_sheet.png")
        if not os.path.exists(sheet_path):
            return
        try:
            sheet = pygame.image.load(sheet_path).convert_alpha()
            self._sheet_images = {
                "down":  self._cut_frames(sheet, 0),
                "left":  self._cut_frames(sheet, 1),
                "right": self._cut_frames(sheet, 2),
                "up":    self._cut_frames(sheet, 3),
            }
            self._sheet_anim_idx   = 0.0
            self._sheet_anim_speed = 0.15
            self._sheet_loaded     = True

            self.image = self._sheet_images["down"][0]
            self.rect  = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))
            self.feet  = pygame.Rect(0, 0, max(1, self.DISPLAY_W // 2), 3)
            self.feet.midbottom = self.rect.midbottom
        except Exception as e:
            print(f"[{self.CHARACTER_NAME}] Sprite sheet non chargée : {e}")

    def _cut_frames(self, sheet, row):
        frames = []
        for frame in range(3):
            x = (self.SPRITE_COLUMN * 3 + frame) * 16
            y = row * 16
            surf = pygame.Surface((16, 16), pygame.SRCALPHA)
            surf.blit(sheet, (0, 0), (x, y, 16, 16))
            frames.append(surf)
        return frames

    def handle_input(self, keys):
        super().handle_input(keys)
        if keys[pygame.K_z]:
            self._current_dir = "up"
        elif keys[pygame.K_s]:
            self._current_dir = "down"
        elif keys[pygame.K_q]:
            self._current_dir = "left"
        elif keys[pygame.K_d]:
            self._current_dir = "right"

    def _update_animation(self, dt):
        if not self._sheet_loaded:
            super()._update_animation(dt)
            return
        frames = self._sheet_images[self._current_dir]
        if self._moving:
            self._sheet_anim_idx += self._sheet_anim_speed
            if self._sheet_anim_idx >= len(frames):
                self._sheet_anim_idx = 0.0
        else:
            self._sheet_anim_idx = 0.0
        self.image = frames[int(self._sheet_anim_idx)]

    def activate_power(self):
        return False

    def update_power(self):
        now = time.time()
        if self.power_active and now - self._power_start >= self.POWER_DURATION:
            self.power_active    = False
            self.cooldown_active = True
            self._power_start    = now
        elif self.cooldown_active and now - self._power_start >= self.POWER_COOLDOWN:
            self.cooldown_active = False

    def get_power_status(self):
        now = time.time()
        if self.power_active:
            return True, False, max(0.0, self.POWER_DURATION - (now - self._power_start))
        elif self.cooldown_active:
            return False, True, max(0.0, self.POWER_COOLDOWN - (now - self._power_start))
        return False, False, 0.0

    def update(self, dt=None):
        super().update(dt)
        self.update_power()

class Mahe(MAMPlayer):
    SPRITE_COLUMN     = 0
    CHARACTER_NAME    = "Mahe"
    POWER_NAME        = "Uppercut"
    POWER_DESCRIPTION = "+6 degats melee pendant 60s"

    def activate_power(self):
        if self.power_active or self.cooldown_active:
            return False
        self.power_active = True
        self._power_start = time.time()
        return True

    def shoot(self, mouse_pos, enemies=None):
        import math
        weapon = self.get_equipped_weapon()
        if weapon and weapon.attack_type == "melee" and enemies is not None:
            origin  = pygame.Vector2(self.rect.centerx, self.rect.centery)
            target  = pygame.Vector2(mouse_pos)
            direction = target - origin
            if direction.length_squared() > 0:
                direction = direction.normalize()
            min_dot = math.cos(math.radians(weapon.melee_arc_deg / 2))
            bonus = 6 if self.power_active else 0
            for enemy in enemies:
                to_e = pygame.Vector2(enemy.x, enemy.y) - origin
                dist = to_e.length()
                if dist > 0 and dist <= (weapon.melee_range + enemy.radius):
                    if direction.dot(to_e.normalize()) >= min_dot:
                        enemy.health -= weapon.melee_damage + bonus
            w_item = self.equipment["weapon"]
            if w_item:
                w_item.durability = max(0, w_item.durability - 1)
                if w_item.durability == 0:
                    self.equipment["weapon"] = None
            return []
        return super().shoot(mouse_pos, enemies)

class Maelys(MAMPlayer):
    SPRITE_COLUMN     = 2
    CHARACTER_NAME    = "Maelys"
    POWER_NAME        = "Bouclier"
    POWER_DESCRIPTION = "Reduit les degats de moitie pendant 60s"

    def activate_power(self):
        if self.power_active or self.cooldown_active:
            return False
        self.power_active = True
        self._power_start = time.time()
        return True

    def take_damage(self, amount, attacker_x=None, attacker_y=None):
        if self.power_active:
            amount = max(1, amount // 2)
        super().take_damage(amount, attacker_x, attacker_y)

class Anthonin(MAMPlayer):
    SPRITE_COLUMN     = 1
    CHARACTER_NAME    = "Anthonin"
    POWER_NAME        = "Invisibilite"
    POWER_DESCRIPTION = "Zombies ignores pendant 60s"

    def activate_power(self):
        if self.power_active or self.cooldown_active:
            return False
        self.power_active = True
        self._power_start = time.time()
        return True

    @property
    def is_invisible(self):
        return self.power_active
