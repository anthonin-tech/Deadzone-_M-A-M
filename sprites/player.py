import pygame
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from systems.inventory import Inventory
from sprites.weapon import Weapon

class Player:
    def __init__(self, x=400, y=300):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 80

        self.health = 100
        self.max_health = 100
        self.lost_health = 1

        self.thirst = 50
        self.max_thirst = 50
        self.lost_thirst = 0.03

        self.hunger = 50
        self.max_hunger = 50
        self.lost_hunger = 0.03

        self.is_hit = False
        self.hit_flash_duration = 0.2
        self.hit_timer = 0

        self.knockback_velocity = pygame.Vector2(0, 0)
        self.knockback_strength = 200

        self.last_shot_time = 0

        self.original_color = (50, 100, 255)
        self.hit_color = (255, 255, 255)

        self.image = pygame.Surface((32, 32))
        self.image.fill(self.original_color)
        self.rect = self.image.get_rect(center=self.position)

        self.inventory = Inventory(capacity=35)

        self.equipment = {
            "weapon": None,
            "helmet": None,
            "chestplate": None,
            "boots": None
        }

        self._add_test_items()
        
    def _add_test_items(self):
        self.inventory.add_item("Fusil à pompe", "arme", "épique", "Pompe_Arme.png" ,"Arme très puissante au corp à corp")
        self.inventory.add_item("Pistolet", "arme", "rare", "Pistolet_Arme.png", "Arme a semi_distance")
        self.inventory.add_item("Hache", "arme", "rare", "Hache_Arme.png", "Arme de corps à corps")
        self.inventory.add_item("Bandage", "soin", "commun", "Bandage_Soin.png", "Soigne 12 PV", effect=7, quantity=4)
        self.inventory.add_item("Kit", "soin", "légendaire", "Kit_Soin.png", "Soigne 30 PV", effect=30, quantity=2)
        self.inventory.add_item("Eau", "boisson", "rare", "Eau_Nourriture.png", "Hydrate de 12", effect=12, quantity=4)
        self.inventory.add_item("Viande", "nourriture", "rare", "", "Rassasit de 12", effect=12, quantity=4  )
        self.inventory.add_item("Casque - Masque à gaz", "armure", "épique", "Casque_Soldat_Armure.png", "Protège la tête et du gaz")
        self.inventory.add_item("Plastron - Haut de Soldat", "armure", "épique", "Tshirt_Soldat_Armure.png", "Protection solide d'un ancien soldat")
        self.inventory.add_item("Botte - Bas de Soldat", "armure", "épique", "Jean_Soldat_Armure.png", "Protection solide d'un ancien soldat")

    def take_damage(self, amount, attacker_x=None, attacker_y=None):
        self.health = max(0, self.health - amount)

        self.is_hit = True
        self.hit_timer = self.hit_flash_duration

        if attacker_x is not None and attacker_y is not None:
            dx = self.position.x - attacker_x
            dy = self.position.y - attacker_y
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance > 0:
                self.knockback_velocity.x = (dx / distance) * self.knockback_strength
                self.knockback_velocity.y = (dy / distance) * self.knockback_strength
        
        print(f"💔 Joueur blessé ! Vie: {self.health}/{self.max_health}")
    
    def get_equipped_weapon(self):
        weapon_item = self.equipment["weapon"]
        if weapon_item is None:
            return None
        return Weapon.from_item(weapon_item)
    
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
                to_enemy = pygame.Vector2(enemy.x, enemy.y) - origin
                dist = to_enemy.length()
                if dist == 0:
                    continue

                if dist <= (weapon.melee_range + enemy.radius):
                    if direction.dot(to_enemy.normalize()) >= min_dot:
                        enemy.health -= weapon.melee_damage

            return []

        return weapon.shoot(origin, target)

    def handle_input(self, keys):
        self.velocity.x = 0
        self.velocity.y = 0

        if keys[pygame.K_z]:
            self.velocity.y = -1
        
        if keys[pygame.K_s]:
            self.velocity.y = 1

        if keys[pygame.K_q]:
            self.velocity.x = -1
        
        if keys[pygame.K_d]:
            self.velocity.x = 1
        
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize()
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        print(f"💚 Joueur soigné ! Vie: {self.health}/{self.max_health}")

    def drink(self, amount):
        self.thirst = min(self.max_thirst, self.thirst + amount)
        print(f"💧 Joueur a bu ! Soif: {self.thirst}/{self.max_thirst}")

    def eat(self, amount):
        self.hunger = min(self.max_hunger, self.hunger + amount)
        print(f"🍖 Joueur a mangé ! Faim: {self.hunger}/{self.max_hunger}")

    def use_item(self, item):
        actions = {
            "soin": self.heal,
            "boisson": self.drink,
            "nourriture": self.eat 
        }

        action = actions.get(item.category)
        if action:
            action(item.effect)
            self.inventory.remove_item(item, 1)
        else:
            print("❌ Objet non utilisable")

    def equip_item(self, item, slot):
        if slot not in self.equipment:
            print(f"❌ Slot invalide: {slot}")
            return False

        if self.equipment[slot] is not None:
            old_item = self.equipment[slot]
            self.inventory.add_item(
                name=old_item.name,
                category=old_item.category,
                rarity=old_item.rarity,
                illustration=old_item.illustration,
                description=old_item.description,
                durability=old_item.durability,
                effect=old_item.effect,
                quantity=1
            )
        
        self.equipment[slot] = item
        self.inventory.remove_item(item, quantity = 1)
        print(f"⚔️ {item.name} équipé dans {slot}")
        return True
    
    def unequip_item(self, slot):
        if slot not in self.equipment:
            print(f"❌ Slot invalide: {slot}")
            return False
        
        if self.equipment[slot] is None:
            print(f"❌ Aucun item équipé dans {slot}")
            return False
        
        item = self.equipment[slot]

        success = self.inventory.add_item(
            name=item.name,
            category=item.category,
            rarity=item.rarity,
            illustration=item.illustration,
            description=item.description,
            durability=item.durability,
            effect=item.effect,
            quantity=1
        )

        if success:
            self.equipment[slot] = None
            print(f"🎒 {item.name} déséquipé de {slot}")
            return True
        else:
            print(f"❌ Inventaire plein, impossible de déséquiper")
            return False
    
    def update(self, dt):
        self.position += self.velocity * self.speed * dt
        
        self.position += self.knockback_velocity * dt

        self.knockback_velocity *= 0.85 

        if self.knockback_velocity.length() < 1:
            self.knockback_velocity.x = 0
            self.knockback_velocity.y = 0
        
        self.rect.center = self.position

        if self.is_hit:
            self.hit_timer -= dt  
            
            if self.hit_timer <= 0:
                self.is_hit = False
                self.image.fill(self.original_color)
            else:
                self.image.fill(self.hit_color)
        
        self.hunger -= self.lost_hunger * dt
        self.hunger = max(0, min(self.hunger, self.max_hunger))

        self.thirst -= self.lost_thirst * dt
        self.thirst = max(0, min(self.thirst, self.max_thirst))

        if self.thirst == 0 or self.hunger == 0:
            self.health -= self.lost_health * dt
            self.health = max(0, min(self.health, self.max_health))
        return self.health
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
        self._draw_health_bar(screen)
        self._draw_needs_bar(screen)

        if self.equipment["weapon"]:
            self._draw_weapon(screen)
    
    def _draw_weapon(self, screen):
        weapon = self.equipment["weapon"]

        weapon_x = self.rect.right + 2 
        weapon_y = self.rect.centery - 10

        weapon_size = (24, 24)
        weapon_image = pygame.transform.scale(weapon.image_surface, weapon_size)

        screen.blit(weapon_image, (weapon_x, weapon_y))
        
    def _draw_health_bar(self, screen):
        bar_width = 40
        bar_height = 5
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 10

        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        health_width = int(bar_width * (self.health / self.max_health))
        health_color = (0, 255, 0) if self.health > 10 else (255, 165, 0) if self.health > 5 else (255, 0, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))

        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

    def _draw_needs_bar(self, screen):
        bar_width = 120
        bar_height = 10
        margin = 10

        screen_height = screen.get_height()

        thirst_y = screen_height - margin - bar_height
        hunger_y = thirst_y - bar_height - 5
        bar_x = margin

        pygame.draw.rect(screen, (80, 80, 80), (bar_x, thirst_y, bar_width, bar_height))
        pygame.draw.rect(screen, (80, 80, 80), (bar_x, hunger_y, bar_width, bar_height))

        thirst_width = int(bar_width * (self.thirst / self.max_thirst))
        hunger_width = int(bar_width * (self.hunger / self.max_hunger))

        pygame.draw.rect(screen, (0, 150, 255), (bar_x, thirst_y, thirst_width, bar_height))
        pygame.draw.rect(screen, (255, 180, 0), (bar_x, hunger_y, hunger_width, bar_height))

        pygame.draw.rect(screen, (255, 255, 255), (bar_x, thirst_y, bar_width, bar_height), 1)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, hunger_y, bar_width, bar_height), 1)
