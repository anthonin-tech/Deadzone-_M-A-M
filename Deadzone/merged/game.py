import pygame
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sprites.player import Player


class Game:

    def __init__(self):
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Deadzone - Survie Zombie")

        self.clock = pygame.time.Clock()
        self.FPS   = 60

        self.player = None
        self.items_to_drop = []

        # Démarre sur le menu principal
        from scenes.menu import MenuScene
        self.current_scene = MenuScene(self)

    def change_scene(self, new_scene):
        self.current_scene = new_scene

    def go_to_menu(self):
        from scenes.menu import MenuScene
        self.current_scene = MenuScene(self)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(self.FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        from scenes.menu import MenuScene
                        if isinstance(self.current_scene, MenuScene):
                            running = False
                        else:
                            self.go_to_menu()
                    else:
                        self.current_scene.handle_event(event)
                else:
                    self.current_scene.handle_event(event)

            self.current_scene.update(dt)
            self.current_scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()
