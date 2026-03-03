<<<<<<< HEAD
import pygame
import sys
from pathlib import Path

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
=======
from map import MapManager
from sprites.player import Player 
import pygame, pyscroll, pytmx, os

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800,700))
        pygame.display.set_caption("MAM")

        self.player = Player(0, 0)
        self.map_manager = MapManager(self.screen, self.player)


    def handle_input(self):
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_z]:
            self.player.move_up()
        elif pressed[pygame.K_s]:
            self.player.move_down()
        elif pressed[pygame.K_q]:
            self.player.move_left()
        elif pressed[pygame.K_d]:
            self.player.move_right()

    def update(self):
        self.map_manager.update()

    def run(self):

        clock = pygame.time.Clock()

        running = True

        while running:

            self.player.save_location()
            self.handle_input()
            self.update()
            self.map_manager.draw()
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            clock.tick(60)

        pygame.quit()
>>>>>>> Maëlys
