import pygame
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from systems.inventory import Inventory

class Player:
    def __init__(self, x=400, y=300):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 200

        self.health = 20
        self.max_health = 20

        self.image = pygame.Surface((32, 32))
        self.image.fill((50, 100, 255))
        self.rect = self.image.get_rect(center=self.position)

        self.inventory = Inventory(capacity=20)

        self.equipment = {
            "weapon": None,
            "helmet": None,
            "chestplate": None,
            "boots": None
        }

        self._add_test_items()
    
    def _add_test_items(self):
        self.inventory.add_item("Fusil à pompe", 100, "arme", "épique", "Pompe_Arme.png" ,"Arme très puissante au corp à corp")
        self.inventory.add_item("Pistolet", 70, "arme", "rare", "Pistolet_Arme.png", "Arme a semi_distance")
        self.inventory.add_item("Bandage", 100, "soin", "commun", "Bandage_Soin.png", "Soigne 5 PV", quantity=5)
        self.inventory.add_item("Kit", 100, "soin", "légendaire", "Kit_Soin.png", "Soigne 20 PV",)
        self.inventory.add_item("Eau", 100, "nourriture", "rare", "Eau_Nourriture.png", "Hydrate de 5", quantity=3)
        self.inventory.add_item("Casque en fer", 100, "armure", "rare", "Bandage_Soin.png", "Protège la tête")
        self.inventory.add_item("Plastron en cuir", 80, "armure", "commun", "Kit_Soin.png", "Protection basique du torse")
        self.inventory.add_item("Bottes renforcées", 90, "armure", "épique", "Eau_Nourriture.png", "Bottes résistantes")

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
        
    def update(self, dt):
        self.position += self.velocity * self.speed * dt
        self.rect.center = self.position
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self._draw_health_bar(screen)

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

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        print(f"💔 Joueur blessé ! Vie: {self.health}/{self.max_health}")
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        print(f"💚 Joueur soigné ! Vie: {self.health}/{self.max_health}")

    def equip_item(self, item, slot):
        if slot not in self.equipment:
            print(f"❌ Slot invalide: {slot}")
            return False

        if self.equipment[slot] is not None:
            old_item = self.equipment[slot]
            self.inventory.add_item(
                old_item.name,
                old_item.durability,
                old_item.category,
                old_item.rarity,
                old_item.illustration,
                old_item.description
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
            item.name,
            item.durability,
            item.category,
            item.rarity,
            item.illustration,
            item.description
        )

        if success:
            self.equipment[slot] = None
            print(f"🎒 {item.name} déséquipé de {slot}")
            return True
        else:
            print(f"❌ Inventaire plein, impossible de déséquiper")
            return False