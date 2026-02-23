import pygame
import sys
import random
import math
from pathlib import Path
from sprites.projectile import Projectile

sys.path.insert(0, str(Path(__file__).parent.parent))


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 55
        self.radius = 10
        self.color = (255, 0, 0)

        self.health = 20
        self.max_health = 20

        self.detection_radius = 200
        self.attack_distance = 50
        self.damage = 10
        self.attack_cooldown = 1000
        self.last_attack = 0

    def _get_player_pos(self, player):
        if hasattr(player, "position"):
            return player.position.x, player.position.y
        return player.x, player.y

    def calculate_distance(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        return math.sqrt(dx**2 + dy**2)

    def move_towards(self, target_x, target_y, dt):
        distance = self.calculate_distance(target_x, target_y)
        if distance > 0:
            dx = (target_x - self.x) / distance
            dy = (target_y - self.y) / distance
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt

    def can_attack(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_attack >= self.attack_cooldown

    def attack(self, player):
        if self.can_attack():
            player.take_damage(self.damage, self.x, self.y)
            self.last_attack = pygame.time.get_ticks()

    def update(self, dt, player, enemies=None, projectiles=None):
        px, py = self._get_player_pos(player)
        distance = self.calculate_distance(px, py)

        if distance <= self.attack_distance:
            self.attack(player)
        elif distance <= self.detection_radius:
            self.move_towards(px, py, dt)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


class FastEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 90
        self.health = 25
        self.max_health = 25
        self.color = (255, 165, 0)


class TankEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 35
        self.health = 120
        self.max_health = 120
        self.damage = 20
        self.attack_cooldown = 1500
        self.radius = 14
        self.color = (120, 0, 0)


class BossEnemy(Enemy):
    IDLE = "idle"
    CHASE = "chase"
    CASTING = "casting"
    RECOVERY = "recovery"

    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 30
        self.health = 250
        self.max_health = 250
        self.damage = 40
        self.radius = 20
        self.color = (0, 0, 0)

        self.state = self.IDLE
        self.phase = 1
        self.cast_skill = None
        self.cast_end_time = 0
        self.recovery_end_time = 0
        self.last_special_time = 0
        self.global_special_cd = 1500

        self.skill_order = ["projectile", "aoe", "summon"]
        self.skill_index = 0
        self.skill_data = {
            "aoe": {"cooldown": 6000, "last_used": -99999, "cast": 800, "recover": 600, "phase_min": 1},
            "summon": {"cooldown": 12000, "last_used": -99999, "cast": 1200, "recover": 900, "phase_min": 2},
            "projectile": {"cooldown": 3500, "last_used": -99999, "cast": 500, "recover": 400, "phase_min": 1},
        }

    def update_phase(self):
        hp_ratio = self.health / self.max_health
        if hp_ratio <= 0.4:
            self.phase = 3
        elif hp_ratio <= 0.7:
            self.phase = 2
        else:
            self.phase = 1

    def pick_next_ready_skill(self, now):
        for i in range(len(self.skill_order)):
            idx = (self.skill_index + i) % len(self.skill_order)
            name = self.skill_order[idx]
            data = self.skill_data[name]
            ready_cd = (now - data["last_used"]) >= data["cooldown"]
            phase_ok = self.phase >= data["phase_min"]
            if ready_cd and phase_ok:
                self.skill_index = (idx + 1) % len(self.skill_order)
                return name
        return None

    def begin_cast(self, skill_name, now):
        self.state = self.CASTING
        self.cast_skill = skill_name
        self.cast_end_time = now + self.skill_data[skill_name]["cast"]

    def do_aoe(self, player):
        px, py = self._get_player_pos(player)
        aoe_radius = 120
        dist = self.calculate_distance(px, py)
        if dist <= aoe_radius:
            player.take_damage(35 if self.phase < 3 else 50, self.x, self.y)

    def do_summon(self, enemies):
        normal_count = 3 if self.phase == 2 else 4
        fast_count = 2 if self.phase == 2 else 3

        for _ in range(normal_count):
            enemies.append(Enemy(self.x + random.randint(-70, 70), self.y + random.randint(-70, 70)))

        for _ in range(fast_count):
            enemies.append(FastEnemy(self.x + random.randint(-70, 70), self.y + random.randint(-70, 70)))

    def do_projectile(self, projectiles, player):
        if hasattr(player, "position"):
            px, py = player.position.x, player.position.y
        else:
            px, py = player.x, player.y

        shots = 1 if self.phase < 3 else 3
        base_angle = math.atan2(py - self.y, px - self.x)
        spread = 0.20
        speed = 300

        for i in range(shots):
            offset = (i - (shots - 1) / 2) * spread
            angle = base_angle + offset

            direction = pygame.Vector2(
                math.cos(angle),
                math.sin(angle)
            )

            projectile = Projectile(
                self.x,
                self.y,
                direction,
                speed=speed,
                damage=20 if self.phase < 3 else 30,
                radius=6,
                color=(40, 40, 40),
                max_distance=900
            )

            projectiles.append(projectile)

    def execute_cast(self, player, enemies, projectiles, now):
        if self.cast_skill == "aoe":
            self.do_aoe(player)
        elif self.cast_skill == "summon":
            self.do_summon(enemies)
        elif self.cast_skill == "projectile":
            self.do_projectile(projectiles, player)

        self.skill_data[self.cast_skill]["last_used"] = now
        self.last_special_time = now
        self.state = self.RECOVERY
        self.recovery_end_time = now + self.skill_data[self.cast_skill]["recover"]
        self.cast_skill = None

    def update(self, dt, player, enemies=None, projectiles=None):
        now = pygame.time.get_ticks()
        self.update_phase()

        if self.state == self.CASTING:
            if now >= self.cast_end_time:
                self.execute_cast(player, enemies, projectiles, now)
            return

        if self.state == self.RECOVERY:
            if now >= self.recovery_end_time:
                self.state = self.IDLE
            return

        px, py = self._get_player_pos(player)
        dist = self.calculate_distance(px, py)
        self.state = self.CHASE if dist <= self.detection_radius else self.IDLE

        if self.state == self.CHASE and dist > self.attack_distance:
            self.move_towards(px, py, dt)

        can_global = (now - self.last_special_time) >= self.global_special_cd
        if can_global:
            skill = self.pick_next_ready_skill(now)
            if skill is not None:
                self.begin_cast(skill, now)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        if self.state == self.CASTING and self.cast_skill == "aoe":
            pygame.draw.circle(screen, (255, 120, 120), (int(self.x), int(self.y)), 120, 2)