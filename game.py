import pygame
import sys
from pathlib import Path

# Ajouter le dossier racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from sprites.player import Player
from scenes.gameplay_scene import Gameplay_Scene


class Game:
    
    def __init__(self):
        pygame.init()
        
        info = pygame.display.Info()
        self.SCREEN_WIDTH = info.current_w
        self.SCREEN_HEIGHT = info.current_h
        
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Deadzone M-A-M - Survie Zombie")
        
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        self.player = Player(x=640, y=360)
        
        self.current_scene = Gameplay_Scene(self, self.player)
        
        print("🎮 Jeu initialisé !")
        print(f"📊 Résolution: {self.screen.get_width()}x{self.screen.get_height()}")
        print(f"🎒 Inventaire: {len(self.player.inventory)}/{self.player.inventory.capacity} items")
    
    def change_scene(self, new_scene):
        self.current_scene = new_scene
        print(f"🔄 Changement de scène: {new_scene.__class__.__name__}")

    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(self.FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.current_scene.handle_event(event)
                else:
                    self.current_scene.handle_event(event)

            self.current_scene.update(dt)

            self.current_scene.draw(self.screen)

            self._draw_fps()

            pygame.display.flip()

        print("👋 Fermeture du jeu...")
        pygame.quit()
        sys.exit()
    
    def _draw_fps(self):
        """Affiche le FPS dans le coin supérieur droit"""
        font = pygame.font.Font(None, 24)
        fps = int(self.clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 0))
        self.screen.blit(fps_text, (self.screen.get_width() - 80, 10))