import os
import sys
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sprites.player import Mahé, Maelys, Anthonin
from game import Game

pygame.init()

WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🧟 DEADZONE GAME 🧟")
CLOCK = pygame.time.Clock()

FONT = pygame.font.Font(None, 40)
BIG_FONT = pygame.font.Font(None, 70)

WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
DARK = (20, 20, 20)
RED = (180, 0, 0)
GREEN = (0, 180, 0)

MENU = "menu"
CHARACTER = "character"
HELP = "help"

state = MENU
player = None



class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self):
        mouse = pygame.mouse.get_pos()
        color = GRAY

        if self.rect.collidepoint(mouse):
            color = GREEN

        pygame.draw.rect(SCREEN, color, self.rect, border_radius=8)
        pygame.draw.rect(SCREEN, WHITE, self.rect, 2, border_radius=8)

        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        SCREEN.blit(text_surface, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)



btn_play = Button("Jouer", 300, 200, 300, 50)
btn_char = Button("Choisir personnage", 300, 270, 300, 50)
btn_help = Button("Aide", 300, 340, 300, 50)
btn_quit = Button("Quitter", 300, 410, 300, 50)

btn_back = Button("Retour", 20, 520, 150, 50)

btn_mahe = Button("Mahé", 350, 200, 200, 50)
btn_maelys = Button("Maëlys", 350, 270, 200, 50)
btn_anthonin = Button("Anthonin", 350, 340, 200, 50)



def draw_title():
    title = BIG_FONT.render("DEADZONE GAME", True, RED)
    SCREEN.blit(title, title.get_rect(center=(WIDTH // 2, 100)))



def menu_screen():
    draw_title()
    btn_play.draw()
    btn_char.draw()
    btn_help.draw()
    btn_quit.draw()



def character_screen():
    draw_title()
    btn_mahe.draw()
    btn_maelys.draw()
    btn_anthonin.draw()
    btn_back.draw()



def help_screen():
    draw_title()

    lines = [
        "Flèches : déplacement",
        "P : pause",
        "ESC : retour au menu"
    ]

    for i, line in enumerate(lines):
        text = FONT.render(line, True, WHITE)
        SCREEN.blit(text, (260, 230 + i * 50))

    btn_back.draw()



running = True

while running:

    SCREEN.fill(DARK)

    if state == MENU:
        menu_screen()

    elif state == CHARACTER:
        character_screen()

    elif state == HELP:
        help_screen()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                state = MENU

       
        if state == MENU:

            if btn_play.is_clicked(event):
                if player:
                    game = Game(SCREEN, player)
                    game.run()
                else:
                    print("⚠️ Choisis un personnage avant de jouer")

            if btn_char.is_clicked(event):
                state = CHARACTER

            if btn_help.is_clicked(event):
                state = HELP

            if btn_quit.is_clicked(event):
                running = False

        elif state == CHARACTER:

            if btn_mahe.is_clicked(event):
                player = Mahé()
                state = MENU

            if btn_maelys.is_clicked(event):
                player = Maelys()
                state = MENU

            if btn_anthonin.is_clicked(event):
                player = Anthonin()
                state = MENU

            if btn_back.is_clicked(event):
                state = MENU

      
        elif state == HELP:

            if btn_back.is_clicked(event):
                state = MENU

    pygame.display.flip()
    CLOCK.tick(60)

pygame.quit()
sys.exit()