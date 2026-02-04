import pygame
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

class InventoryScene:
    def __init__(self, game, player):
        self.game = game
        self.player = player

        self.slot_size = 64
        self.margin = 10
        self.cols = 5

        self.equipment_slot_size = 56

        self.character_panel_x = 50
        self.character_panel_y = 150
        self.character_panel_width = 300
        self.character_panel_height = 450

        total_width = self.cols * self.slot_size + (self.cols - 1) * self.margin
        self.start_x = self.character_panel_x + self.character_panel_width + 50
        self.start_y = 150

        self.bg_color = (40, 40, 50)
        self.slot_color = (60, 60, 70)
        self.slot_border_color = (100, 100, 110)

        self.rarity_colors = {
            "commun": (200, 200, 200),
            "rare": (100, 150, 255),
            "épique": (200, 100, 255),
            "légendaire": (255, 200, 50)
        }

        self.font_quantity = pygame.font.Font(None, 24)
        self.font_tooltip = pygame.font.Font(None, 28)
        self.font_title = pygame.font.Font(None, 48)
        self.font_info = pygame.font.Font(None, 20)

        self.tooltip_surface = None
        self.tooltip_pos = (0, 0)
        self.hovered_item = None

        self.selected_item_index = None

        self._load_item_images()

    def _load_item_images(self):
        for item in self.player.inventory.items:
            if item.image_surface is None:
                try:
                    img_path = Path("assets/items") / item.illustration
                    item.image_surface = pygame.image.load(str(img_path)).convert_alpha()
                    item.image_surface = pygame.transform.scale(
                        item.image_surface,
                        (self.slot_size - 8, self.slot_size - 8)
                    )
                except (FileNotFoundError, pygame.error):
                    print(f"⚠️ Image non trouvée: {item.illustration}")
                    item.image_surface = pygame.Surface((self.slot_size - 8, self.slot_size - 8))
                    item.image_surface.fill((150, 150, 150))
                    font = pygame.font.Font(None, 40)
                    text = font.render("?", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(self.slot_size // 2 - 4, self.slot_size // 2 - 4))
                    item.image_surface.blit(text, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
                from scenes.gameplay_scene import Gameplay_Scene
                self.game.change_scene(Gameplay_Scene(self.game, self.player))
        
        elif event.type == pygame.K_e:
            if self.hovered_item:
                self._equip_hovered_item()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_click(event.pos)
            elif event.button == 3:
                self.handle_right_click(event.pos)
    
    def _equip_hovered_item(self):
        if not self.hovered_item:
            return
        
        item = self.hovered_item

        if item.category == "arme":
            self.player.equip_item(item, "weapon")
            self._load_item_images()
        
        elif item.category == "armure":
            if "casque" in item.name.lower() or "helmet" in item.name.lower():
                self.player.equip_item(item, "helmet")
            elif "plastron" in item.name.lower() or "chestplate" in item.name.lower():
                self.player.equip_item(item, "chestplate")
            elif "botte" in item.name.lower() or "boots" in item.name.lower():
                self.player.equip_item(item, "boots")
            self._load_item_images()

    def handle_click(self, mouse_pos):
        mx, my = mouse_pos

        equipement_slots = {
            "helmet": (self.character_panel_x + 180, self.character_panel_y + 50),
            "chestplate": (self.character_panel_x + 180, self.character_panel_y + 120),
            "boots": (self.character_panel_x + 180, self.character_panel_y + 190),
            "weapon": (self.character_panel_x + 180, self.character_panel_y + 260)
        }

        for slot_name, (slot_x, slot_y) in equipement_slots.items():
            rect = pygame.Rect(slot_x, slot_y, self.equipment_slot_size, self.equipment_slot_size)
            if rect.collidepoint(mx, my):
                if self.player.equipment[slot_name] is not None:
                    self.player.unequip_item(slot_name)
                    self._load_item_images()
                return
            
        for i, item in enumerate(self.player.inventory.items):
            col = i % self.cols
            row = i // self.cols

            x = self.start_x + col * (self.slot_size + self.margin)
            y = self.start_y + row * (self.slot_size + self.margin)

            rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            if rect.collidepoint(mx, my):
                print(f"🖱️ Clic gauche : {item.name} (quantité: {item.quantity})")
                if item.category == "soin":
                    self.player.heal(5)
                    self.player.inventory.remove_item(item, quantity=1)
                    if item.quantity <= 0:
                        self._load_item_images()
                break
    
    def handle_right_click(self, mouse_pos):
        mx, my = mouse_pos
        for i, item in enumerate(self.player.inventory.items):
            col = i % self.cols
            row = i // self.cols

            x = self.start_x + col * (self.slot_size + self.margin)
            y = self.start_y + row * (self.slot_size + self.margin)

            rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            if rect.collidepoint(mx, my):
                print(f"🗑️ Clic droit : Jeter {item.name}")
                self.player.inventory.remove_item(item, quantity=1)
                if item not in self.player.inventory.items:
                    self._load_item_images()
                break

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.tooltip_surface = None
        self.hovered_item = None

        for i, item in enumerate(self.player.inventory.items):
            col = i % self.cols
            row = i // self.cols
            x = self.start_x + col * (self.slot_size + self.margin)
            y = self.start_y + row * (self.slot_size + self.margin)

            rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            if rect.collidepoint(mx, my):
                self.hovered_item = item
                self._create_tooltip(item, mx, my)
                break
    
    def _create_tooltip(self, item, mx, my):
        color = self.rarity_colors.get(item.rarity, (255, 255, 255))

        lines = [
            f"{item.name}",
            f"Description: {item.description}",
            f"Rareté: {item.rarity.capitalize()}",
            f"Catégorie: {item.category}",
            f"Durabilité: {item.durability}%",
            f"Quantité: {item.quantity}"
        ]

        if item.category == "soin" or item.category == "nourriture":
            lines.append("Clic gauche pour utiliser")
        
        if item.category == "arme" or item.category == "armure":
            lines.append("Clic sur [E] pour équiper")
        padding = 10
        line_height = 25
        tooltip_width = 220
        tooltip_height = len(lines) * line_height + padding * 2

        self.tooltip_surface = pygame.Surface((tooltip_width, tooltip_height))
        self.tooltip_surface.fill((30, 30, 40))
        pygame.draw.rect(self.tooltip_surface, color, (0, 0, tooltip_width, tooltip_height), 2)

        for i, line in enumerate(lines):
            if i == 0:
                text = self.font_tooltip.render(line, True, color)
            else:
                text = self.font_info.render(line, True, (200, 200, 200))
            self.tooltip_surface.blit(text, (padding, padding + i * line_height))
        
        self.tooltip_pos = (mx + 15, my + 15)
        if self.tooltip_pos[0] + tooltip_width > self.game.screen.get_width():
            self.tooltip_pos = (mx - tooltip_width - 15, my + 15)
        if self.tooltip_pos[1] + tooltip_height > self.game.screen.get_height():
            self.tooltip_pos = (self.tooltip_pos[0], my - tooltip_height - 15)
    
    def draw(self, screen):
        screen.fill(self.bg_color)

        title = self.font_title.render("INVENTAIRE", True, (220, 220, 220))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 60))

        info_text = self.font_info.render(
            f"Slots: {len(self.player.inventory.items)}/{self.player.inventory.capacity}  |  "
            f"TAB pour fermer  |  Clic droit pour jeter  |  [E] pour équiper",
            True, (180, 180, 180)
        )

        screen.blit(info_text, (screen.get_width()//2 - info_text.get_width()//2, 110))

        self._draw_character_panel(screen)

        for i in range(self.player.inventory.capacity):
            col = i % self.cols
            row = i // self.cols

            x = self.start_x + col * (self.slot_size + self.margin)
            y = self.start_y + row * (self.slot_size + self.margin)

            pygame.draw.rect(screen, self.slot_color, (x, y, self.slot_size, self.slot_size))

            border_width = 3 if (i < len(self.player.inventory.items) and 
                                 self.player.inventory.items[i] == self.hovered_item) else 2
            pygame.draw.rect(screen, self.slot_border_color, 
                           (x, y, self.slot_size, self.slot_size), border_width)

            if i < len(self.player.inventory.items):
                item = self.player.inventory.items[i]

                if item.image_surface:
                    screen.blit(item.image_surface, (x + 4, y + 4))
                
                if item.quantity > 1:
                    qty_text = self.font_quantity.render(
                        str(item.quantity), True, (255, 255, 0)
                    )

                    qty_bg = pygame.Surface((qty_text.get_width() + 4, qty_text.get_height() + 2))
                    qty_bg.fill((0, 0, 0))
                    qty_bg.set_alpha(150)
                    screen.blit(qty_bg,
                              (x + self.slot_size - qty_text.get_width() - 6, 
                               y + self.slot_size - qty_text.get_height() - 4))
                    screen.blit(qty_text, 
                              (x + self.slot_size - qty_text.get_width() - 4, 
                               y + self.slot_size - qty_text.get_height() - 4))
                
                if item.durability < 100:
                    durability_width = int((self.slot_size - 8) * (item.durability / 100))
                    durability_color = (0, 255, 0) if item.durability > 50 else \
                                      (255, 165, 0) if item.durability > 25 else (255, 0, 0)

                    pygame.draw.rect(screen, (50, 50, 50), 
                                   (x + 4, y + self.slot_size - 8, self.slot_size - 8, 4))
                    pygame.draw.rect(screen, durability_color, 
                                   (x + 4, y + self.slot_size - 8, durability_width, 4))

        if self.tooltip_surface:
            screen.blit(self.tooltip_surface, self.tooltip_pos)
    
    def _draw_character_panel(self, screen):
        panel_rect = pygame.Rect(
            self.character_panel_x,
            self.character_panel_y,
            self.character_panel_width,
            self.character_panel_height
        )
        pygame.draw.rect(screen, (50, 50, 60), panel_rect)
        pygame.draw.rect(screen, (100, 100, 110), panel_rect, 2)

        panel_title = self.font_tooltip.render("PERSONNAGE", True, (220, 220, 220))
        screen.blit(panel_title, (self.character_panel_x + 10, self.character_panel_y + 10))

        char_x = self.character_panel_x + 60
        char_y = self.character_panel_y + 80

        pygame.draw.circle(screen, (255, 200, 150), (char_x, char_y), 20)
        pygame.draw.rect(screen, (50, 100, 255), (char_x - 15, char_y + 20, 30, 50))
        pygame.draw.rect(screen, (50, 100, 255), (char_x - 30, char_y + 25, 15, 35))
        pygame.draw.rect(screen, (50, 100, 255), (char_x + 15, char_y + 25, 15, 35))
        pygame.draw.rect(screen, (40, 80, 200), (char_x - 12, char_y + 70, 10, 40))
        pygame.draw.rect(screen, (40, 80, 200), (char_x + 2, char_y + 70, 10, 40))

        if self.player.equipment["helmet"]:
            pygame.draw.circle(screen, (150, 150, 150), (char_x, char_y - 5), 23, 3)
        if self.player.equipment["chestplate"]:
            pygame.draw.rect(screen, (180, 180, 180), (char_x - 18, char_y + 20, 36, 50), 3)
        if self.player.equipment["boots"]:
            pygame.draw.rect(screen, (100, 100, 100), (char_x - 12, char_y + 100, 10, 15))
            pygame.draw.rect(screen, (100, 100, 100), (char_x + 2, char_y + 100, 10, 15))

        if self.player.equipment["weapon"]:
            weapon = self.player.equipment["equipment"]
            weapon_x = char_x + 30
            weapon_y = char_y + 40

            if "fusil" in weapon.name.lower() or "pompe" in weapon.name.lower():
                pygame.draw.rect(screen, (100, 50, 0), (weapon_x, weapon_y - 2, 25, 4))
                pygame.draw.circle(screen, (150, 75, 0), (weapon_x + 25, weapon_y), 3)
            elif "pistolet" in weapon.name.lower():
                pygame.draw.rect(screen, (80, 80, 80), (weapon_x, weapon_y - 2, 15, 4))
                pygame.draw.rect(screen, (60, 60, 60), (weapon_x, weapon_y - 4, 8, 8))
            else:
                pygame.draw.rect(screen, (128, 128, 128), (weapon_x, weapon_y - 2, 20, 4))

        equipment_slots = {
            "helmet": ("Casque", self.character_panel_y + 50),
            "chestplate": ("Plastron", self.character_panel_y + 120),
            "boots": ("Bottes", self.character_panel_y + 190),
            "weapon": ("Arme", self.character_panel_y + 260)
        }

        slot_x = self.character_panel_x = 160

        for slot_name, (label, slot_y) in equipment_slots.items():
            label_text = self.font_info.render(label, True, (200, 200, 200))
            screen.blit(label_text, (slot_x, slot_y - 20))

            pygame.draw.rect(screen, self.slot_border_color, (slot_x, slot_y, self.equipment_slot_size, self.equipment_slot_size))
            pygame.draw.rect(screen, self.slot_border_color, (slot_x, slot_y, self.equipment_slot_size, self.equipment_slot_size), 2)

            equipped_item = self.player.equipment[slot_name]
            if equipped_item:
                if equipped_item.image_surface is None:
                    try:
                        img_path = Path("assets/items") / equipped_item.illustration
                        equipped_item.image_surface = pygame.image.load(str(img_path)).convert_alpha()
                        equipped_item.image_surface = pygame.transform.scale(
                            equipped_item.image_surface,
                            (self.equipment_slot_size - 8, self.equipment_slot_size - 8)
                        )
                    except (FileNotFoundError, pygame.error):
                        equipped_item.image_surface = pygame.Surface((self.equipment_slot_size - 8, self.equipment_slot_size - 8))
                        equipped_item.image_surface.fill((150, 150, 150))
            
                if equipped_item.image_surface:
                    screen.blit(equipped_item.image_surface, (slot_x + 4, slot_y + 4))
