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

        total_width = self.cols * self.slot_size + (self.cols - 1) * self.margin
        self.start_x = (game.screen.get_width() - total_width) // 2
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
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_click(event.pos)
            elif event.button == 3:
                self.handle_right_click(event.pos)
        
    def handle_click(self, mouse_pos):
        mx, my = mouse_pos
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
            f"Rareté: {item.rarity.capitalize()}",
            f"Catégorie: {item.category}",
            f"Durabilité: {item.durability}%",
            f"Quantité: {item.quantity}"
        ]

        if item.category == "soin":
            lines.append("Clic gauche pour utiliser")

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
            f"TAB/ESC pour fermer  |  Clic droit pour jeter",
            True, (180, 180, 180)
        )
        screen.blit(info_text, (screen.get_width()//2 - info_text.get_width()//2, 110))

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