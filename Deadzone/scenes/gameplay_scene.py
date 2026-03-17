import pygame, copy
import math
import sys
import os
import json
import random
from pathlib import Path
from sprites.chest import Chest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scenes.inventory_scene import InventoryScene
from sprites.dropped_item import DroppedItem
from sprites.item import Items
from sprites.library_item import ITEMS_BY_NAME
from sprites.enemy import BossEnemy, Enemy, FastEnemy, TankEnemy

MAP_ZOOM = 3
SAVE_FILE = "savegame.json"

class Gameplay_Scene:

    def __init__(self, game, player):
        self.game   = game
        self.player = player
        self.paused = False

        self.enemies       = []
        self.dropped_items = []
        self.chests        = []
        self.projectiles   = []

        self.nearby_item   = None
        self.nearby_chest  = None
        self.enemies_killed = 0
        self.start_time    = pygame.time.get_ticks()

        self.bg_color    = (30, 80, 30)
        self.font        = pygame.font.Font(None, 24)
        self.font_pickup = pygame.font.Font(None, 28)

        self._spawn_timer    = 0
        self._spawn_interval = 15

        self.map_manager = None
        self._try_init_map()

        self._spawn_enemies()
        self._load_chests_from_map()
        self._spawn_ground_items()

    def _try_init_map(self):
        import traceback
        try:
            from map import MapManager, MAP_AVAILABLE, ASSET_DIR, PROJECT_ROOT
            if MAP_AVAILABLE and os.path.exists(os.path.join(ASSET_DIR, "map.tmx")):
                old_cwd = os.getcwd()
                os.chdir(PROJECT_ROOT)
                try:
                    self.map_manager = MapManager(self.game.screen, self.player)
                finally:
                    os.chdir(old_cwd)

                if not self.map_manager.maps:
                    self.map_manager = None

        except Exception as e:
            traceback.print_exc()
            self.map_manager = None

        if self.map_manager:
            self.map_manager.on_map_change = self._on_map_changed

    def _on_map_changed(self, new_map_name):
        self.enemies.clear()
        zones = self.map_manager.get_spawn_zones()
        TYPES = [Enemy, Enemy, Enemy, FastEnemy, TankEnemy]
        for zone in zones:
            nb = random.randint(2, 4)
            for _ in range(nb):
                x = random.randint(zone.left + 8, max(zone.left + 9, zone.right  - 8))
                y = random.randint(zone.top  + 8, max(zone.top  + 9, zone.bottom - 8))
                self.enemies.append(random.choice(TYPES)(x, y))

    def world_to_screen(self, wx, wy):
        if not self.map_manager:
            return int(wx), int(wy)
        pcx, pcy = self.map_manager.get_player_screen_pos()
        sx = int((wx - self.player.position.x) * MAP_ZOOM + pcx)
        sy = int((wy - self.player.position.y) * MAP_ZOOM + pcy)
        return sx, sy

    def screen_to_world(self, sx, sy):
        if not self.map_manager:
            return float(sx), float(sy)
        pcx, pcy = self.map_manager.get_player_screen_pos()
        wx = self.player.position.x + (sx - pcx) / MAP_ZOOM
        wy = self.player.position.y + (sy - pcy) / MAP_ZOOM
        return wx, wy

    def _player_screen_pos(self):
        if self.map_manager:
            return self.map_manager.get_player_screen_pos()
        return self.player.rect.centerx, self.player.rect.centery

    def _spawn_enemies(self):
        px = self.player.position.x
        py = self.player.position.y
        self.enemies.append(BossEnemy  (px + 200, py + 150))
        self.enemies.append(Enemy      (px - 180, py -  90))
        self.enemies.append(FastEnemy  (px + 220, py - 170))
        self.enemies.append(TankEnemy  (px - 160, py + 200))

        if self.map_manager:
            zones = self.map_manager.get_spawn_zones()
            TYPES = [Enemy, Enemy, Enemy, FastEnemy, TankEnemy]
            for zone in zones:
                nb = random.randint(2, 4)
                for _ in range(nb):
                    x = random.randint(zone.left + 8, max(zone.left + 9, zone.right  - 8))
                    y = random.randint(zone.top  + 8, max(zone.top  + 9, zone.bottom - 8))
                    self.enemies.append(random.choice(TYPES)(x, y))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.game.change_scene(InventoryScene(self.game, self.player, return_scene=self))
            if event.key == pygame.K_e:
                if self.nearby_chest:
                    from scenes.chest_scene import ChestScene
                    self.nearby_chest.open()
                    self.game.change_scene(ChestScene(self.game, self.player, self.nearby_chest, return_scene=self))
                else:
                    self.try_pickup_item()
            if event.key == pygame.K_h:
                self.player.take_damage(5, 400, 300)
            if event.key == pygame.K_j:
                self.player.heal(5)
            if event.key == pygame.K_p:
                if hasattr(self.player, "activate_power"):
                    activated = self.player.activate_power()
                    if activated:
                        name = getattr(self.player, "POWER_NAME", "Pouvoir")
            if event.key == pygame.K_F5:
                self.save_game()
            if event.key == pygame.K_m:
                self.paused = not self.paused

    def try_pickup_item(self):
        if not self.nearby_item:
            return
        ok = self.player.inventory.add_item(self.nearby_item.item)
        if ok:
            self.dropped_items.remove(self.nearby_item)
            self.nearby_item = None

    def _respawn_enemies(self):
        if not self.map_manager:
            return
        zones = self.map_manager.get_spawn_zones()
        if not zones:
            return
        TYPES = [Enemy, TankEnemy, FastEnemy]
        for zone in zones:
            nb = random.randint(1, 2)
            for _ in range(nb):
                x = random.randint(zone.left + 8, max(zone.left + 9, zone.right  - 8))
                y = random.randint(zone.top  + 8, max(zone.top  + 9, zone.bottom - 8))
                self.enemies.append(random.choice(TYPES)(x, y))

    def update(self, dt):
        if self.paused:
            return

        keys = pygame.key.get_pressed()
        self.player.save_location()
        self.player.handle_input(keys)
        self.player.update(dt)

        if self.map_manager:
            self.map_manager.update()

        for item in self.dropped_items:
            item.update(dt)

        self.update_enemies(dt)
        self.update_projectiles(dt)
        self.check_nearby_items()
        self.check_nearby_chests()

        if hasattr(self.game, "items_to_drop") and self.game.items_to_drop:
            for item in self.game.items_to_drop:
                self.dropped_items.append(
                    DroppedItem(item, self.player.position.x + 50, self.player.position.y))
            self.game.items_to_drop.clear()

        if self.player.health <= 0:
            from scenes.gameover_scene import GameOverScene
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
            self.game.player = self.player
            self.game.change_scene(GameOverScene(self.game, {
                "enemies_killed": self.enemies_killed,
                "time_survived":  elapsed
            }))
            return

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            world_target = self.screen_to_world(mx, my)
            self.projectiles.extend(self.player.shoot(world_target, enemies=self.enemies))
            self._remove_dead_enemies()

        self._spawn_timer += dt
        if self._spawn_timer >= self._spawn_interval:
            self._spawn_timer = 0
            self._respawn_enemies()

    def check_nearby_chests(self):
        self.nearby_chest = None
        if not self.map_manager:
            return
        current = self.map_manager.current_map
        px, py = self.player.position.x, self.player.position.y
        for chest in self.chests:
            if getattr(chest, 'map_name', None) == current and chest.is_near(px, py):
                self.nearby_chest = chest
                break

    def _load_chests_from_map(self):
        if not self.map_manager:
            return
        for map_name, map_obj in self.map_manager.maps.items():
            for obj in map_obj.tmx_data.objects:
                obj_name = getattr(obj, "name", "") or ""
                if "chest" in obj_name.lower():
                    items = self._default_chest_items(obj_name)
                    chest = Chest(x=obj.x, y=obj.y, items=items)
                    chest.map_name = map_name 
                    self.chests.append(chest)

    def _default_chest_items(self, chest_name: str):
        name = chest_name.lower()
        if "cave_1" in name:
            keys = ["BANDAGE","MEAT", "WOOD", "WOOD", "WOOD","WOOD", "FABRIC"]
        elif "cave_2" in name:
            keys = ["MEAT", "MEAT", "WATER","REINFORCED_WOOD", "IRON"]
        elif "cave_3" in name:
            keys = ["IRON","IRON","IRON", "HETMET_SOLDAT","ADHESIVE_TAPE","CARE_KIT"]
        elif "map_1" in name:
            keys = ["TSHIRT", "BANDAGE", "WATER"]
        elif "map_2" in name:
            keys = ["PANTS", "WOOD", "WOOD", "WEED", "WEED", "WEED", "WEED", "WEED",]
        elif "map_3" in name:
            keys = ["CAP", "WATER","WATER", "MEAT", "AXE"]
        elif "map_4" in name:
            keys = ["FIBER", "FIBER","WOOD", "WOOD", "MEAT","FABRIC"]
        elif "bunker" in name:
            keys = ["ADHESIVE_TAPE", "WATER","GUN", "WOOD", "WOOD","BANDAGE"]
        elif "camp" in name:
            keys = ["REINFORCED_WOOD", "MEAT", "FABRIC"]
        elif "church" in name:
            keys = ["WEED", "WEED","BOTTS_SOLDAT", "BANDAGE", "BANDAGE","AHESIVE_TAPE"]
        elif "canteen" in name:
            keys = ["MEAT","MEAT","MEAT", "WATER", "WATER"]
        elif "class" in name:
            keys = ["ADHESIVE_TAPE", "CHESPLATE_SOLDAT","CARE_KIT"]
        elif "desk" in name:
            keys = ["WEED", "WEED", "REINFORCED_WOOD","BANDAGE"]
        return [copy.copy(ITEMS_BY_NAME[k]) for k in keys if k in ITEMS_BY_NAME]

    def _remove_dead_enemies(self):
        for e in self.enemies[:]:
            if e.health <= 0:
                self.enemies.remove(e)
                self.enemies_killed += 1

    def check_nearby_items(self):
        self.nearby_item = None
        current = self.map_manager.current_map if self.map_manager else None
        px, py = self.player.position.x, self.player.position.y
        closest = float("inf")
        for dropped in self.dropped_items:
            item_map = getattr(dropped, 'map_name', None)
            if item_map is not None and item_map != current:
                continue
            dist = math.hypot(dropped.x - px, dropped.y - py)
            if dist < closest and dropped.is_near(px, py):
                closest = dist
                self.nearby_item = dropped

    def _spawn_ground_items(self):
        if not self.map_manager:
            return

        spawn_config = {
            "map": [
                ("WEED", 1, 4, 20),
                ("WOOD", 1, 3, 20),
            ],
            "cave-2": [
                ("IRON", 1, 2, 10),
            ],
        }

        

        for map_name, spawn_table in spawn_config.items():
            if map_name not in self.map_manager.maps:
                continue

            map_obj = self.map_manager.maps[map_name]
            walls   = map_obj.walls
            map_w   = map_obj.tmx_data.width  * map_obj.tmx_data.tilewidth
            map_h   = map_obj.tmx_data.height * map_obj.tmx_data.tileheight

            zones = self.map_manager.maps[map_name].item_spawn_zones
            if not zones:
                continue

            for key, qty_min, qty_max, count in spawn_table:
                if key not in ITEMS_BY_NAME:
                    continue
                spawned  = 0
                attempts = 0
                while spawned < count and attempts < count * 20:
                    attempts += 1
                    zone = random.choice(zones)
                    x = random.uniform(zone.left, zone.right)
                    y = random.uniform(zone.top, zone.bottom)
                    item_rect = pygame.Rect(x - 8, y - 8, 16, 16)
                    if item_rect.collidelist(walls) != -1:
                        continue
                    item          = copy.copy(ITEMS_BY_NAME[key])
                    item.quantity = random.randint(qty_min, qty_max)
                    dropped       = DroppedItem(item, x, y)
                    dropped.map_name = map_name
                    self.dropped_items.append(dropped)
                    spawned += 1

    def update_enemies(self, dt):
        walls = self.map_manager.get_walls() if self.map_manager else []
        player_invisible = getattr(self.player, "is_invisible", False)
        for enemy in self.enemies[:]:
            enemy._walls = walls
            if player_invisible:
                enemy.update(dt, None, self.enemies, self.projectiles)
            else:
                enemy.update(dt, self.player, self.enemies, self.projectiles)
            if enemy.health <= 0 and enemy in self.enemies:
                self.enemies.remove(enemy)
                self.enemies_killed += 1

    def update_projectiles(self, dt):
        for proj in self.projectiles[:]:
            proj.update(dt)
            if not proj.alive:
                if proj in self.projectiles:
                    self.projectiles.remove(proj)
                continue

            if self.map_manager:
                proj_rect = pygame.Rect(
                    int(proj.position.x) - proj.radius,
                    int(proj.position.y) - proj.radius,
                    proj.radius * 2,
                    proj.radius * 2
                )
                if proj_rect.collidelist(self.map_manager.get_walls()) != -1:
                    proj.alive = False
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    continue

            if proj.owner == "player":
                for enemy in self.enemies[:]:
                    if pygame.Vector2(enemy.x, enemy.y).distance_to(proj.position) <= (enemy.radius + proj.radius):
                        enemy.health -= proj.damage
                        enemy.take_hit()
                        proj.alive = False
                        if enemy.health <= 0 and enemy in self.enemies:
                            self.enemies.remove(enemy)
                            self.enemies_killed += 1
                        break

            elif proj.owner == "enemy":
                player_pos = pygame.Vector2(self.player.position.x, self.player.position.y)
                if player_pos.distance_to(proj.position) <= (8 + proj.radius):
                    self.player.take_damage(proj.damage, proj.position.x, proj.position.y)
                    proj.alive = False

            if not proj.alive and proj in self.projectiles:
                self.projectiles.remove(proj)

    def draw(self, screen):
        if self.map_manager:
            self.map_manager.draw()
        else:
            screen.fill(self.bg_color)

        for dropped in self.dropped_items:
            item_map = getattr(dropped, 'map_name', None)
            if item_map is not None and self.map_manager and item_map != self.map_manager.current_map:
                continue
            sx, sy = self.world_to_screen(dropped.x, dropped.y)
            if dropped.image:
                draw_y = sy + dropped.float_offset
                screen.blit(dropped.image, (sx, draw_y))

        zoom = MAP_ZOOM if self.map_manager else 1
        for enemy in self.enemies:
            sx, sy = self.world_to_screen(enemy.x, enemy.y)
            enemy.draw(screen, sx, sy, zoom)

        if not self.map_manager:
            self.player.draw(screen)
        else:
            pcx, pcy = self._player_screen_pos()
            sprite_half_h = (16 * MAP_ZOOM) // 2
            self.player._draw_health_bar(screen, sx=pcx, sy=pcy - sprite_half_h - 10)
            self.player._draw_needs_bar(screen)
            if self.player.equipment["weapon"]:
                self.player._draw_weapon(screen, cx=pcx, cy=pcy)

        for proj in self.projectiles:
            sx, sy = self.world_to_screen(proj.position.x, proj.position.y)
            proj.draw(screen, sx, sy, zoom)

        self._draw_aim_preview(screen)

        if self.nearby_item:
            self.draw_pickup_prompt(screen)

        if self.nearby_chest and not self.nearby_chest.is_open:
            self.draw_chest_prompt(screen)

        self._draw_power_hud(screen)

        if self.paused:
            pause_bg = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pause_bg.fill((0, 0, 0, 180))
            screen.blit(pause_bg, (0, 0))
            self._draw_instructions(screen)

    def _draw_power_hud(self, screen):
        if not hasattr(self.player, "get_power_status"):
            return
        power_active, cooldown_active, remaining = self.player.get_power_status()
        power_name = getattr(self.player, "POWER_NAME", "Pouvoir")
        power_desc = getattr(self.player, "POWER_DESCRIPTION", "")

        font = pygame.font.Font(None, 22)
        sw = screen.get_width()
        x, y = sw - 230, 10

        if power_active:
            color = (80, 255, 80)
            label = f"[P] {power_name} : {remaining:.0f}s"
        elif cooldown_active:
            color = (255, 160, 40)
            label = f"[P] Recharge : {remaining:.0f}s"
        else:
            color = (160, 160, 255)
            label = f"[P] {power_name} : pret"

        bg = pygame.Surface((220, 38), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        screen.blit(bg, (x - 5, y - 4))
        surf = font.render(label, True, color)
        screen.blit(surf, (x, y))
        if power_desc:
            d = font.render(power_desc, True, (140, 140, 140))
            screen.blit(d, (x, y + 16))

    def draw_chest_prompt(self, screen):
        chest = self.nearby_chest
        sx, sy = self.world_to_screen(chest.x + chest.width // 2, chest.y - 10)
        rendered = self.font_pickup.render("[E] Ouvrir", True, (225, 192, 70))
        tx = sx - rendered.get_width() // 2
        ty = sy - rendered.get_height() // 10
        bg = pygame.Surface((rendered.get_width() + 10, rendered.get_height() + 6))
        bg.fill((0, 0, 0)); bg.set_alpha(180)
        screen.blit(bg, (tx - 5, ty - 3))
        screen.blit(rendered, (tx, ty))

    def draw_pickup_prompt(self, screen):
        sx, sy = self.world_to_screen(
            self.nearby_item.x + self.nearby_item.width // 2,
            self.nearby_item.y - 10)
        text = f"[E] {self.nearby_item.item.name}"
        rendered = self.font_pickup.render(text, True, (255, 255, 255))
        tx = sx - rendered.get_width() // 1.2
        ty = sy - rendered.get_height() // 10
        bg = pygame.Surface((rendered.get_width() + 10, rendered.get_height() + 6))
        bg.fill((0, 0, 0)); bg.set_alpha(180)
        screen.blit(bg,       (tx - 5, ty - 3))
        screen.blit(rendered, (tx, ty))

    def _draw_instructions(self, screen):
        lines = [
            "ZQSD : Déplacer",
            "TAB : Inventaire",
            "E : Ramasser / Ouvrir coffre",
            "Clic gauche : Tirer / Attaquer",
            "P : Pouvoir spécial",
            "M : Pause",
            "F5 : Sauvegarder",
        ]
        y_start = screen.get_height() // 2 - (len(lines) * 15)
        for i, line in enumerate(lines):
            surf = self.font.render(line, True, (255, 255, 255))
            x = screen.get_width() // 2 - surf.get_width() // 2
            y = y_start + i * 30
            screen.blit(surf, (x, y))

    def _draw_aim_preview(self, screen):
        weapon = self.player.get_equipped_weapon()
        if weapon is None:
            return
        if weapon.attack_type != "melee" and not pygame.mouse.get_pressed()[0]:
            return

        pcx, pcy = self._player_screen_pos()
        origin_s = pygame.Vector2(pcx, pcy)
        mx, my   = pygame.mouse.get_pos()
        direction = pygame.Vector2(mx, my) - origin_s
        if direction.length_squared() == 0:
            return
        direction = direction.normalize()

        scale = MAP_ZOOM if self.map_manager else 1

        if weapon.attack_type == "melee":
            reach_px  = int(weapon.melee_range * scale)
            base_angle = math.atan2(direction.y, direction.x)
            half_arc   = math.radians(weapon.melee_arc_deg / 2)
            steps = 18
            points = [(int(origin_s.x), int(origin_s.y))]
            for i in range(steps + 1):
                t = i / steps
                angle = (base_angle - half_arc) + (2 * half_arc * t)
                points.append((int(origin_s.x + math.cos(angle) * reach_px),
                               int(origin_s.y + math.sin(angle) * reach_px)))
            cone = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pygame.draw.polygon(cone, (255, 200, 120,  90), points)
            pygame.draw.polygon(cone, (255, 230, 170, 180), points, 2)
            screen.blit(cone, (0, 0))
        else:
            max_dist_px = min(int(weapon.max_distance * scale), 500)
            end_pos = origin_s + direction * max_dist_px
            pygame.draw.line(screen, (255, 255, 255),
                             (int(origin_s.x), int(origin_s.y)),
                             (int(end_pos.x),  int(end_pos.y)), 2)
            if weapon.pellets > 1:
                base_angle  = math.atan2(direction.y, direction.x)
                half_spread = math.radians(weapon.spread_deg / 2)
                spread_dist = min(max_dist_px, 300)
                for sign in (-1, 1):
                    a = base_angle + sign * half_spread
                    ep = origin_s + pygame.Vector2(math.cos(a), math.sin(a)) * spread_dist
                    pygame.draw.line(screen, (255, 200, 120),
                                     (int(origin_s.x), int(origin_s.y)),
                                     (int(ep.x), int(ep.y)), 1)

    def save_game(self):
        inventory_items = []
        for item in self.player.inventory.items:
            if item:
                for key, value in ITEMS_BY_NAME.items():
                    if value.name == item.name:
                        inventory_items.append(key)

        dropped_items = []
        for dropped in self.dropped_items:
            for key, value in ITEMS_BY_NAME.items():
                if value.name == dropped.item.name:
                    dropped_items.append({
                        "id": key,
                        "x": dropped.x,
                        "y": dropped.y
                    })

        enemies_data = []
        for enemy in self.enemies:
            enemies_data.append({
                "type": enemy.__class__.__name__,
                "x": enemy.x,
                "y": enemy.y,
                "health": enemy.health
            })

        chests_data = []
        for chest in self.chests:
            chest_items = []
            for item in chest.items:
                for key, value in ITEMS_BY_NAME.items():
                    if value.name == item.name:
                        chest_items.append(key)

            chests_data.append({
            "id": chest.id,
            "x": chest.x,
            "y": chest.y,
            "items": chest_items
        })

        data = {
            "player_class": self.player.__class__.__name__,
            "player_x": self.player.position.x,
            "player_y": self.player.position.y,
            "player_health": self.player.health,
            "inventory": inventory_items,
            "dropped_items": dropped_items,
            "enemies": enemies_data,
            "enemies_killed": self.enemies_killed,
            "time": pygame.time.get_ticks() - self.start_time,
            "chests": chests_data
        }

        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            return

        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        player_class_name = data.get("player_class")
        player_class = globals().get(player_class_name)
        if player_class:
            self.player = player_class()

        self.player.position.x = data["player_x"]
        self.player.position.y = data["player_y"]
        self.player.rect.centerx = int(self.player.position.x)
        self.player.rect.centery = int(self.player.position.y)
        self.player.health = data["player_health"]

        self.player.inventory.items.clear()
        for item_id in data.get("inventory", []):
            item = ITEMS_BY_NAME.get(item_id)
            if item:
                self.player.inventory.add_item(copy.copy(item))

        self.dropped_items.clear()
        for dropped in data.get("dropped_items", []):
            item = ITEMS_BY_NAME.get(dropped["id"])
            if item:
                self.dropped_items.append(
                    DroppedItem(copy.copy(item), dropped["x"], dropped["y"])
                )

        self.enemies.clear()
        for enemy_data in data.get("enemies", []):
            enemy_class = globals().get(enemy_data["type"])
            if enemy_class:
                enemy = enemy_class(enemy_data["x"], enemy_data["y"])
                enemy.health = enemy_data["health"]
                self.enemies.append(enemy)

        self.enemies_killed = data["enemies_killed"]
        self.start_time = pygame.time.get_ticks() - data["time"]


        for chest_data in data.get("chests", []):
            for chest in self.chests:
             if chest.id == chest_data["id"]:
                chest.items.clear()

                for item_id in chest_data["items"]:
                    item = ITEMS_BY_NAME.get(item_id)
                    if item:
                        chest.items.append(copy.copy(item))