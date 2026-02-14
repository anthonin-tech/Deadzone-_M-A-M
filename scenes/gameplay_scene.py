import pygame
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from scenes.inventory_scene import InventoryScene
from sprites.dropped_item import DroppedItem
from sprites.item import Items
from sprites.enemy import Enemy

class Gameplay_Scene:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.enemies = []
        self.dropped_items = []
        
        self.bg_color = (30, 80, 30)
        
        self.font = pygame.font.Font(None, 24)
        self.font_pickup = pygame.font.Font(None, 28)

        self.nearby_item = None

        self.enemies_killed = 0
        self.start_time = pygame.time.get_ticks()

        self._spawn_test_items()
        self._spawn_enemies()

    def _spawn_enemies(self):
        """Crée quelques ennemis pour tester"""
        self.enemies.append(Enemy(100, 100))
        self.enemies.append(Enemy(700, 500))

    def _spawn_test_items(self):
        """Crée quelques items au sol pour tester"""
        item1 = Items(
            name="Kit",
            durability=100,
            category="soin",
            rarity="légendaire",
            illustration="Kit_Soin.png",
            description="Restaure 20 PV",
            quantity=1
        )
        
        item2 = Items(
            name="Fusil à pompe",
            durability=80,
            category="arme",
            rarity="épique",
            illustration="Pompe_Arme.png",
            description="Dégâts: 25",
            quantity=1
        )
        
        item3 = Items(
            name="Bouteille d'eau",
            durability=100,
            category="nourriture",
            rarity="commun",
            illustration="Eau_Nourriture.png",
            description="Hydratation de 5",
            quantity=1
        )
        
        # Place les items à différentes positions
        self.dropped_items.append(DroppedItem(item1, 200, 150))
        self.dropped_items.append(DroppedItem(item2, 400, 300))
        self.dropped_items.append(DroppedItem(item3, 600, 200))
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB: 
                self.game.change_scene(InventoryScene(self.game, self.player))
            
            if event.key == pygame.K_e:
                self.try_pickup_item()

            if event.key == pygame.K_h:
                attacker_x = 400
                attacker_y = 300
                self.player.take_damage(5, attacker_x, attacker_y)
            
            if event.key == pygame.K_j:
                self.player.heal(5)
    
    def try_pickup_item(self):
        if self.nearby_item:
            succes = self.player.inventory.add_item(
                name=self.nearby_item.item.name,
                durability = self.nearby_item.item.durability,
                category = self.nearby_item.item.category,
                rarity=self.nearby_item.item.rarity,
                illustration=self.nearby_item.item.illustration,
                description=self.nearby_item.item.description,
                quantity=self.nearby_item.item.quantity
            )

            if succes:
                self.dropped_items.remove(self.nearby_item)
                self.nearby_item = None
                print(f"✅ Item ramassé !")
            else:
                print(f"❌ Inventaire plein ! ")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(dt)
        
        self.player.update(dt)

        for item in self.dropped_items:
            item.update(dt)
        
        self.update_enemies(dt)
        
        self.check_nearby_items()

        if hasattr(self.game, 'items_to_drop') and self.game.items_to_drop:
            for item in self.game.items_to_drop:
                drop_x = self.player.x + 50
                drop_y = self.player.y
                self.dropped_items.append(DroppedItem(item, drop_x, drop_y))
            self.game.items_to_drop.clear()
        
        if self.player.health <= 0:
            from scenes.gameover_scene import GameOverScene
            
            time_survived = (pygame.time.get_ticks() - self.start_time) / 1000

            stats = {
                'enemies_killed': self.enemies_killed,
                'time_survived': time_survived
            }

            self.game.change_scene(GameOverScene(self.game, stats))
            return
            

    def check_nearby_items(self):
        self.nearby_item = None

        player_x = self.player.rect.centerx
        player_y = self.player.rect.centery


        closest_distance = float('inf')

        for dropped in self.dropped_items:
            if dropped.is_near(player_x, player_y):
                dx = dropped.x + dropped.width//2 - player_x
                dy = dropped.y + dropped.height//2 - player_y
                distance = (dx**2 + dy**2) ** 0.5

                if distance < closest_distance:
                    closest_distance = distance
                    self.nearby_item = dropped

    def update_enemies(self, dt):
        player_x = self.player.position.x
        player_y = self.player.position.y

        for enemy in self.enemies[:]:   #[:] pour copie si on supprime
            distance = enemy.calculate_distance(player_x, player_y)

            if distance < enemy.detection_radius and distance > enemy.attack_distance:
                enemy.move_towards(player_x, player_y, dt)
            
            elif distance <= enemy.attack_distance and enemy.can_attack():
                self.player.take_damage(enemy.damage, enemy.x, enemy.y)
                enemy.last_attack = pygame.time.get_ticks()
                print(f"💥 Ennemi Attaque ! PV player: {self.player.health}")

            # Update graphique
            enemy.update(dt)

            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.enemies_killed += 1

    def draw(self, screen):
        screen.fill(self.bg_color)

        for dropped in self.dropped_items:
            dropped.draw(screen)
        
        for enemy in self.enemies:
            enemy.draw(screen)

        self.player.draw(screen)
        
        if self.nearby_item:
            self.draw_pickup_prompt(screen)

        self._draw_instructions(screen)

        enemy_text = self.font.render(f"Ennemi: {len(self.enemies)}", True, (255, 255, 255))
        screen.blit(enemy_text, (10, screen.get_height() - 60))
    
    def draw_pickup_prompt(self, screen):
        text = f"[E] {self.nearby_item.item.name}"

        rendered_text = self.font_pickup.render(text, True, (255, 255, 255))
        text_width = rendered_text.get_width()
        text_height = rendered_text.get_height()

        text_x = self.nearby_item.x + self.nearby_item.width//2 - text_width//2
        text_y = self.nearby_item.y - 40

        bg_surface = pygame.Surface((text_width + 10, text_height + 6))
        bg_surface.fill((0, 0, 0))
        bg_surface.set_alpha(180)
        screen.blit(bg_surface, (text_x - 5, text_y - 3))

        screen.blit(rendered_text, (text_x, text_y))

    def _draw_instructions(self, screen):
        instructions = [
            "ZQSD : Déplacer",
            "TAB: Inventaire",
            "E: Ramasser",
            "H : Prendre des dégâts (test)",
            "J : Se soigner (test)",
            "ESC : Quitter"
        ]
        
        y = 10
        for instruction in instructions:
            text = self.font.render(instruction, True, (255, 255, 255))
            screen.blit(text, (10, y))
            y += 25
        
        items_text = self.font.render(
            f"Items: {len(self.player.inventory)}/{self.player.inventory.capacity}", 
            True, (255, 255, 0)
        )
        screen.blit(items_text, (10, screen.get_height() - 30))