import pygame
import pygame
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from systems.crafting_manager import CraftingManager
from sprites.recipes import RECIPES

class CraftScene():
    def __init__(self, game, crafting_manager: CraftingManager):
        self.game = game
        self.cm = crafting_manager
        self.visible = False
        self.hovered_recipe = None

        screen_w =game.screen.get_width()
        panel_w, panel_h = 420, 500
        self.panel_rect = pygame.Rect(
            screen_w - panel_w - 20, 100, panel_w, panel_h
        )

        self.slot_h = 70
        self.scroll_offset = 0

        self.font_title = pygame.font.Font(None, 36)
        self.font_name = pygame.font.Font(None, 26)
        self.font_info = pygame.font.Font(None, 20)
        self.font_hint = pygame.font.Font(None, 22)
    
    def toggle(self):
        self.visible = not self.visible
        self.scroll_offset = 0

    def handle_event(self, event):
        if not self.visible:
            return
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered_recipe = self._recipe_at(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            recipe = self._recipe_at(event.pos)
            if recipe and self.cm.can_craft(recipe):
                self.cm.craft(recipe)
            
        if event.type == pygame.MOUSEWHEEL:
            max_scroll = max(0, len(RECIPES) * self.slot_h - (self.panel_rect - 50))
            self.scroll_offset = max(0, min(
                self.scroll_offset - event.y * self.slot_h,
                max_scroll
            ))

    def _recipe_at(self, pos):
        if not self.panel_rect.collidepoint(pos):
            return None
        rel_y = pos[1] - self.panel_rect.y - 50 + self.scroll_offset
        index = int(rel_y // self.slot_h)
        if 0 <= index < len(RECIPES):
            return RECIPES[index]
        return None
    
    def draw(self, screen):
        if not self.visible:
            return

        pygame.draw.rect(screen, (30, 30, 40), self.panel_rect, border_radius=10)
        pygame.draw.rect(screen, (150, 150, 160), self.panel_rect, 2, border_radius=10)

        title = self.font_title.render("⚒  CRAFT", True, (255, 220, 80))
        screen.blit(title, (self.panel_rect.x + 12, self.panel_rect.y + 10))

        list_rect = pygame.Rect(
            self.panel_rect.x,
            self.panel_rect.y + 50,
            self.panel_rect.width,
            self.panel_rect.height - 50
        )
        screen.set_clip(list_rect)

        for i, recipe in enumerate(RECIPES):
            y = self.panel_rect.y + 50 + i * self.slot_h - self.scroll_offset
            slot_rect = pygame.Rect(
                self.panel_rect.x + 6, y,
                self.panel_rect.width - 12, self.slot_h - 4
            )

            can      = self.cm.can_craft(recipe)
            hovered  = recipe is self.hovered_recipe

            if hovered and can:
                bg = (70, 130, 70)
            elif can:
                bg = (45, 90, 50)
            elif hovered:
                bg = (80, 60, 60)
            else:
                bg = (50, 50, 60)

            pygame.draw.rect(screen, bg, slot_rect, border_radius=6)
            pygame.draw.rect(screen, (100, 100, 110), slot_rect, 1, border_radius=6)

            result    = recipe["result"]
            qty_str   = f"  ×{result['quantity']}" if result["quantity"] > 1 else ""
            name_col  = (255, 255, 255) if can else (110, 110, 110)
            name_surf = self.font_name.render(result["name"] + qty_str, True, name_col)
            screen.blit(name_surf, (slot_rect.x + 8, slot_rect.y + 8))

            ingr_str = "  +  ".join(
                f"{name} ×{qty}" for name, qty in recipe["ingredients"].items()
            )
            ingr_col  = (170, 210, 170) if can else (90, 90, 90)
            ingr_surf = self.font_info.render(ingr_str, True, ingr_col)
            screen.blit(ingr_surf, (slot_rect.x + 8, slot_rect.y + 32))

            if hovered and can:
                hint = self.font_hint.render("Clic pour crafter", True, (200, 255, 200))
                screen.blit(hint, (slot_rect.right - hint.get_width() - 8, slot_rect.y + 28))

        screen.set_clip(None)
            
    