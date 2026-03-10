import pygame
from scenes.menu import Menu

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Deadzone")

    menu = Menu(screen)
    menu.run()