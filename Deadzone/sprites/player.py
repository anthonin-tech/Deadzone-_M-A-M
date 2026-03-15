import pygame
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from systems.inventory import Inventory
from sprites.weapon import Weapon
from sprites.library_item import *

FRAME_W  = 16
FRAME_H  = 16
N_FRAMES = 6
RENDER_SCALE = 1

ANIM_IDLE  = [0, 5]
ANIM_WALK  = [1, 2, 3, 4]
IDLE_SPEED = 0.6
WALK_SPEED = 0.12

class Player(pygame.sprite.Sprite):

    def __init__(self, x=400, y=300):
        super().__init__()

        base_dir   = os.path.dirname(os.path.abspath(__file__))
        asset_dir  = os.path.join(base_dir, "..", "asset")
        sprite_path = os.path.join(asset_dir, "Player.png")

        self._use_sprite = os.path.exists(sprite_path)
        self._frames = []

        if self._use_sprite:
            raw = pygame.image.load(sprite_path).convert_alpha()
            for i in range(N_FRAMES):
                surf = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
                surf.blit(raw, (0, 0), (i * FRAME_W, 0, FRAME_W, FRAME_H))
                self._frames.append(
                    pygame.transform.scale(surf,
                        (FRAME_W * RENDER_SCALE, FRAME_H * RENDER_SCALE))
                )

        self._anim_seq   = ANIM_IDLE
        self._anim_idx   = 0
        self._anim_timer = 0.0
        self._moving     = False
        self._flip_x     = False

        if self._use_sprite:
            self.image = self._frames[ANIM_IDLE[0]]
        else:
            self.image = pygame.Surface(
                (FRAME_W * RENDER_SCALE, FRAME_H * RENDER_SCALE), pygame.SRCALPHA)
            self.image.fill((50, 100, 255))

        self.rect = self.image.get_rect(center=(x, y))

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.speed    = 110

        self.feet = pygame.Rect(0, 0, max(1, int(self.rect.width * 0.5)), 4)
        self.feet.midbottom = self.rect.midbottom
        self.old_position   = [x, y]

        self.health      = 100
        self.max_health  = 100
        self.lost_health = 1

        self.shield      = 0
        self.max_shield  = 0
        self.default_armor_shield_bonus = {
            "helmet": 15, "chestplate": 30, "boots": 15
        }
        self.shield_regen_rate  = 12
        self.shield_regen_delay = 4
        self.time_since_last_damage = 0

        self.thirst      = 50
        self.max_thirst  = 50
        self.lost_thirst = 0.03
        self.hunger      = 50
        self.max_hunger  = 50
        self.lost_hunger = 0.03

        self.is_hit             = False
        self.hit_flash_duration = 0.2
        self.hit_timer          = 0.0

        self.knockback_velocity = pygame.Vector2(0, 0)
        self.knockback_strength = 120
        self.last_shot_time     = 0

        self.inventory = Inventory(capacity=35)
        self.equipment = {
            "weapon": None, "helmet": None,
            "chestplate": None, "boots": None,
        }
        self._add_test_items()

    def _update_animation(self, dt):
        target_seq   = ANIM_WALK  if self._moving else ANIM_IDLE
        target_speed = WALK_SPEED if self._moving else IDLE_SPEED

        if target_seq is not self._anim_seq:
            self._anim_seq   = target_seq
            self._anim_idx   = 0
            self._anim_timer = 0.0

        self._anim_timer += dt
        if self._anim_timer >= target_speed:
            self._anim_timer = 0.0
            self._anim_idx   = (self._anim_idx + 1) % len(self._anim_seq)

        base = self._frames[self._anim_seq[self._anim_idx]]

        if self._flip_x:
            base = pygame.transform.flip(base, True, False)

        if self.is_hit:
            overlay = pygame.Surface(base.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 60, 60, 150))
            result = base.copy()
            result.blit(overlay, (0, 0))
            self.image = result
        else:
            self.image = base

    def save_location(self):
        self.old_position = [self.position.x, self.position.y]

    def move_back(self):
        self.position.x = self.old_position[0]
        self.position.y = self.old_position[1]
        self._sync_rect()

    def _add_test_items(self):
        a = self.inventory.add_item
        a(CARE_KIT)
        a(BANDAGE)
        a(WATER)
        a(MEAT)
        a(SHOTGUN)
        a(GUN)
        a(AXE)
        a(HELMET_SOLDAT)
        a(CHESPLATE_SOLDAT)
        a(BOTTS_SOLDAT)
        a(WOOD)
        a(IRON)
        a(FIBER)
        a(REINFORCED_WOOD)
        a(WEED)
        a(WEED)
        a(WEED)
        a(WEED)
        a(WEED)
        a(WEED)
        a(WEED)
        a(WEED)
        a(SPRING)
        a(ADHESIVE_TAPE)
        a(FABRIC)

    def take_damage(self, amount, attacker_x=None, attacker_y=None):
        remaining = amount
        if self.shield > 0:
            absorbed      = min(self.shield, remaining)
            self.shield  -= absorbed
            remaining    -= absorbed
        if remaining > 0:
            self.health = max(0, self.health - remaining)
        self.time_since_last_damage = 0
        self.is_hit    = True
        self.hit_timer = self.hit_flash_duration
        if attacker_x is not None and attacker_y is not None:
            dx   = self.position.x - attacker_x
            dy   = self.position.y - attacker_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.knockback_velocity.x = (dx / dist) * self.knockback_strength
                self.knockback_velocity.y = (dy / dist) * self.knockback_strength

    def get_equipped_weapon(self):
        item = self.equipment["weapon"]
        return Weapon.from_item(item) if item else None

    def shoot(self, mouse_pos, enemies=None):
        weapon = self.get_equipped_weapon()
        if weapon is None:
            return []
        now = pygame.time.get_ticks()
        if now - self.last_shot_time < weapon.cooldown_ms:
            return []
        self.last_shot_time = now

        origin = pygame.Vector2(self.rect.centerx, self.rect.centery)
        target = pygame.Vector2(mouse_pos)

        w_item = self.equipment["weapon"]
        if w_item:
            w_item.durability = max(0, w_item.durability - 1)
            if w_item.durability == 0:
                self.equipment["weapon"] = None
                return []

        if weapon.attack_type == "melee":
            if enemies is None:
                return []
            direction = target - origin
            if direction.length_squared() == 0:
                direction = pygame.Vector2(1, 0)
            else:
                direction = direction.normalize()
            min_dot = math.cos(math.radians(weapon.melee_arc_deg / 2))
            for enemy in enemies:
                to_e = pygame.Vector2(enemy.x, enemy.y) - origin
                dist = to_e.length()
                if dist > 0 and dist <= (weapon.melee_range + enemy.radius):
                    if direction.dot(to_e.normalize()) >= min_dot:
                        enemy.health -= weapon.melee_damage
            return []

        return weapon.shoot(origin, target)

    def handle_input(self, keys):
        self.velocity.xy = 0, 0
        if keys[pygame.K_z]: self.velocity.y = -1
        if keys[pygame.K_s]: self.velocity.y =  1
        if keys[pygame.K_q]: self.velocity.x = -1
        if keys[pygame.K_d]: self.velocity.x =  1
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize()

        if self.velocity.x < 0:
            self._flip_x = True
        elif self.velocity.x > 0:
            self._flip_x = False
        self._moving = self.velocity.length() > 0

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def drink(self, amount):
        self.thirst = min(self.max_thirst, self.thirst + amount)

    def eat(self, amount):
        self.hunger = min(self.max_hunger, self.hunger + amount)

    def _get_armor_slot_for_item(self, item):
        n = item.name.lower()
        if "casque"   in n or "helmet"     in n: return "helmet"
        if "plastron" in n or "chestplate" in n: return "chestplate"
        if "botte"    in n or "boots"      in n: return "boots"
        return None

    def _get_item_shield_value(self, item, slot=None):
        if item.effect and item.effect > 0:
            return item.effect
        s = slot or self._get_armor_slot_for_item(item)
        return self.default_armor_shield_bonus.get(s, 0) if s else 0

    def _recalculate_shield_from_equipment(self, refill=False):
        old_max = self.max_shield
        new_max = sum(
            self._get_item_shield_value(self.equipment[s], s)
            for s in ("helmet", "chestplate", "boots")
            if self.equipment[s] is not None
        )
        self.max_shield = max(0, new_max)
        if refill and self.max_shield > old_max:
            self.shield = min(self.max_shield,
                              self.shield + (self.max_shield - old_max))
        else:
            self.shield = min(self.shield, self.max_shield)

    def use_item(self, item):
        actions = {"soin": self.heal, "boisson": self.drink, "nourriture": self.eat}
        action = actions.get(item.category)
        if action:
            action(item.effect)
            self.inventory.remove_item(item, 1)

    def equip_item(self, item, slot):
        if slot not in self.equipment:
            return False
        if self.equipment[slot] is not None:
            old = self.equipment[slot]
            self.inventory.add_item(old)
        self.equipment[slot] = item
        self.inventory.remove_item(item, quantity=1)
        if slot in ("helmet", "chestplate", "boots"):
            self._recalculate_shield_from_equipment(refill=True)
        return True

    def unequip_item(self, slot):
        if slot not in self.equipment or self.equipment[slot] is None:
            return False
        item = self.equipment[slot]
        ok = self.inventory.add_item(item)
        if ok:
            self.equipment[slot] = None
            if slot in ("helmet", "chestplate", "boots"):
                self._recalculate_shield_from_equipment(refill=False)
        return ok

    def _sync_rect(self):
        self.rect.center = (int(self.position.x), int(self.position.y))
        self.feet.midbottom = self.rect.midbottom

    def update(self, dt=None):

        if dt is not None:
            self.position += self.velocity * self.speed * dt
            self.position += self.knockback_velocity * dt
            self.knockback_velocity *= 0.85
            if self.knockback_velocity.length() < 1:
                self.knockback_velocity.xy = 0, 0

            if self.is_hit:
                self.hit_timer -= dt
                if self.hit_timer <= 0:
                    self.is_hit = False

            if self._use_sprite:
                self._update_animation(dt)

            self.hunger = max(0, min(self.max_hunger,
                                     self.hunger - self.lost_hunger * dt))
            self.thirst = max(0, min(self.max_thirst,
                                     self.thirst - self.lost_thirst * dt))
            if self.thirst == 0 or self.hunger == 0:
                self.health = max(0, min(self.max_health,
                                         self.health - self.lost_health * dt))

            self.time_since_last_damage += dt
            if (self.max_shield > 0 and self.shield < self.max_shield
                    and self.time_since_last_damage >= self.shield_regen_delay):
                self.shield = min(self.max_shield,
                                  self.shield + self.shield_regen_rate * dt)

        self._sync_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self._draw_health_bar(screen)
        self._draw_needs_bar(screen)
        if self.equipment["weapon"]:
            self._draw_weapon(screen)

    def _draw_weapon(self, screen, cx=None, cy=None):
        item = self.equipment["weapon"]
        if item is None or item.image_surface is None:
            return
        cx = cx if cx is not None else self.rect.centerx
        cy = cy if cy is not None else self.rect.centery
        img = pygame.transform.scale(item.image_surface, (20, 20))
        screen.blit(img, (cx + 22, cy - 10))

    def _draw_health_bar(self, screen, sx=None, sy=None):
        bw, bh = 48, 5
        bx = (sx if sx is not None else self.rect.centerx) - bw // 2
        by = (sy if sy is not None else self.rect.top - 10)

        if self.max_shield > 0:
            shy = by - bh - 2
            pygame.draw.rect(screen, (60, 60, 60),    (bx, shy, bw, bh))
            sw = int(bw * self.shield / self.max_shield)
            pygame.draw.rect(screen, (0, 170, 255),   (bx, shy, sw, bh))
            pygame.draw.rect(screen, (180, 220, 255), (bx, shy, bw, bh), 1)

        pygame.draw.rect(screen, (60, 60, 60), (bx, by, bw, bh))
        hw = int(bw * self.health / self.max_health)
        hc = ((0, 220, 0) if self.health > 60
              else (255, 165, 0) if self.health > 25
              else (220, 0, 0))
        pygame.draw.rect(screen, hc,            (bx, by, hw, bh))
        pygame.draw.rect(screen, (200, 200, 200),(bx, by, bw, bh), 1)

    def _draw_needs_bar(self, screen):
        bw, bh, margin = 120, 10, 10
        sh = screen.get_height()
        ty = sh - margin - bh
        hy = ty - bh - 5
        bx = margin

        pygame.draw.rect(screen, (60, 60, 60),  (bx, ty, bw, bh))
        pygame.draw.rect(screen, (60, 60, 60),  (bx, hy, bw, bh))
        pygame.draw.rect(screen, (0, 150, 255),
                         (bx, ty, int(bw * self.thirst / self.max_thirst), bh))
        pygame.draw.rect(screen, (255, 180, 0),
                         (bx, hy, int(bw * self.hunger / self.max_hunger), bh))
        pygame.draw.rect(screen, (200, 200, 200), (bx, ty, bw, bh), 1)
        pygame.draw.rect(screen, (200, 200, 200), (bx, hy, bw, bh), 1)

        font = pygame.font.Font(None, 18)
        screen.blit(font.render("Soif", True, (160, 210, 255)), (bx + bw + 4, ty))
        screen.blit(font.render("Faim", True, (255, 200, 100)), (bx + bw + 4, hy))
