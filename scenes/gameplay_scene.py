import pygame
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

class Gameplay_Scene:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        
        self.bg_color = (30, 80, 30)
        
        self.font = pygame.font.Font(None, 24)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_TAB, pygame.K_i):
                from scenes.inventory_scene import InventoryScene
                self.game.change_scene(InventoryScene(self.game, self.player))
            
            if event.key == pygame.K_h:
                self.player.take_damage(10)
            
            if event.key == pygame.K_j:
                self.player.heal(15)
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        self.player.update(dt)
    
    def draw(self, screen):
        screen.fill(self.bg_color)
        
        self.player.draw(screen)
        
        self._draw_instructions(screen)
    
    def _draw_instructions(self, screen):
        instructions = [
            "ZQSD : Déplacer",
            "TAB: Inventaire",
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