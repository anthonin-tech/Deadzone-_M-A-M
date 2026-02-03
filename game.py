import pygame
import sys
from pathlib import Path

# Ajouter le dossier racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from sprites.player import Player
from scenes.gameplay_scene import Gameplay_Scene


class Game:
    """Classe principale du jeu"""
    
    def __init__(self):
        # ===== INITIALISATION PYGAME =====
        pygame.init()
        
        # Récupérer les dimensions de l'écran
        info = pygame.display.Info()
        self.SCREEN_WIDTH = info.current_w
        self.SCREEN_HEIGHT = info.current_h
        
        # Créer la fenêtre (mode fenêtré)
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Deadzone M-A-M - Survie Zombie")
        
        # Horloge pour gérer le FPS
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # ===== CRÉER LE JOUEUR =====
        self.player = Player(x=640, y=360)
        
        # ===== SCÈNE ACTUELLE =====
        self.current_scene = Gameplay_Scene(self, self.player)
        
        print("🎮 Jeu initialisé !")
        print(f"📊 Résolution: {self.screen.get_width()}x{self.screen.get_height()}")
        print(f"🎒 Inventaire: {len(self.player.inventory)}/{self.player.inventory.capacity} items")
    
    def change_scene(self, new_scene):
        """Change la scène actuelle"""
        self.current_scene = new_scene
        print(f"🔄 Changement de scène: {new_scene.__class__.__name__}")
    
    def run(self):
        """Boucle principale du jeu"""
        running = True
        
        while running:
            # ===== DELTA TIME =====
            dt = self.clock.tick(self.FPS) / 1000  # Convertir en secondes
            
            # ===== ÉVÉNEMENTS =====
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Touche ESC pour quitter
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        # Passer l'événement à la scène actuelle
                        self.current_scene.handle_event(event)
                else:
                    # Passer tous les autres événements à la scène
                    self.current_scene.handle_event(event)
            
            # ===== MISE À JOUR =====
            self.current_scene.update(dt)
            
            # ===== AFFICHAGE =====
            self.current_scene.draw(self.screen)
            
            # Afficher le FPS
            self._draw_fps()
            
            # Mettre à jour l'affichage
            pygame.display.flip()
        
        # ===== FERMETURE =====
        print("👋 Fermeture du jeu...")
        pygame.quit()
        sys.exit()
    
    def _draw_fps(self):
        """Affiche le FPS dans le coin supérieur droit"""
        font = pygame.font.Font(None, 24)
        fps = int(self.clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 0))
        self.screen.blit(fps_text, (self.screen.get_width() - 80, 10))