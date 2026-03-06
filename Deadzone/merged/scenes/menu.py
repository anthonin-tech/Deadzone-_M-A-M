"""
Menu principal — fusionné base + M-A-M
Sélection de personnage parmi les 3 avatars M-A-M avec portraits.
"""

import pygame
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sprites.characters import Mahe, Maelys, Anthonin


# ------------------------------------------------------------------ #
#  Bouton réutilisable
# ------------------------------------------------------------------ #

class Button:
    def __init__(self, text, x, y, width, height,
                 color=(40, 40, 40), hover_color=(0, 140, 0),
                 text_color=(255, 255, 255)):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, screen, font):
        mouse = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=8)
        text_surf = font.render(self.text, True, self.text_color)
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ------------------------------------------------------------------ #
#  MenuScene
# ------------------------------------------------------------------ #

class MenuScene:

    STATE_MAIN      = "main"
    STATE_CHARACTER = "character"
    STATE_HELP      = "help"

    # (classe, nom affiché, description pouvoir, clé portrait)
    CHARACTERS = [
        (Mahe,     "Mahe",     "Uppercut : +6 degats melee (60s)", "mahe"),
        (Maelys,   "Maelys",   "Bouclier : reduit les degats (60s)", "maelys"),
        (Anthonin, "Anthonin", "Invisibilite : zombies ignores (60s)", "anthonin"),
    ]

    def __init__(self, game):
        self.game = game
        self.state = self.STATE_MAIN
        self.selected_idx = 0  # index dans CHARACTERS

        sw, sh = game.screen.get_size()
        cx = sw // 2

        # Polices
        self._font_title = pygame.font.Font(None, 80)
        self._font_btn   = pygame.font.Font(None, 38)
        self._font_sub   = pygame.font.Font(None, 28)
        self._font_info  = pygame.font.Font(None, 23)

        # Boutons menu principal
        bw, bh, gap = 280, 52, 12
        bx = cx - bw // 2
        self._btn_play  = Button("Jouer",              bx, 230, bw, bh)
        self._btn_char  = Button("Choisir personnage", bx, 230 + (bh+gap),     bw, bh)
        self._btn_help  = Button("Aide",               bx, 230 + (bh+gap)*2,   bw, bh)
        self._btn_quit  = Button("Quitter",            bx, 230 + (bh+gap)*3,   bw, bh,
                                 color=(100, 20, 20), hover_color=(180, 0, 0))

        # Boutons sélection personnage (flèches)
        self._btn_prev = Button("<", cx - 260, sh//2 - 30, 60, 60,
                                color=(50,50,80), hover_color=(80,80,130))
        self._btn_next = Button(">", cx + 200, sh//2 - 30, 60, 60,
                                color=(50,50,80), hover_color=(80,80,130))
        self._btn_select = Button("Choisir ce personnage", cx - 160, sh//2 + 130, 320, 52)

        # Bouton retour
        self._btn_back = Button("<- Retour", 30, sh - 70, 160, 46,
                                color=(60,60,60), hover_color=(90,90,90))

        # Portraits des personnages (agrandis x6 avec pixel art)
        self._portraits = {}
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        asset_dir = os.path.join(base_dir, "asset")
        for _, _, _, key in self.CHARACTERS:
            path = os.path.join(asset_dir, f"portrait_{key}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                # Agrandir x8 en pixel art strict (nearest neighbor, pas de flou)
                img = pygame.transform.scale(img, (128, 128))
                self._portraits[key] = img

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state != self.STATE_MAIN:
                    self.state = self.STATE_MAIN
                return

        if self.state == self.STATE_MAIN:
            if self._btn_play.is_clicked(event):
                self._start_game()
            elif self._btn_char.is_clicked(event):
                self.state = self.STATE_CHARACTER
            elif self._btn_help.is_clicked(event):
                self.state = self.STATE_HELP
            elif self._btn_quit.is_clicked(event):
                pygame.quit()
                sys.exit()

        elif self.state == self.STATE_CHARACTER:
            if self._btn_prev.is_clicked(event):
                self.selected_idx = (self.selected_idx - 1) % len(self.CHARACTERS)
            elif self._btn_next.is_clicked(event):
                self.selected_idx = (self.selected_idx + 1) % len(self.CHARACTERS)
            elif self._btn_select.is_clicked(event):
                self.state = self.STATE_MAIN
            elif self._btn_back.is_clicked(event):
                self.state = self.STATE_MAIN

            # Flèches clavier aussi
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_idx = (self.selected_idx - 1) % len(self.CHARACTERS)
                elif event.key == pygame.K_RIGHT:
                    self.selected_idx = (self.selected_idx + 1) % len(self.CHARACTERS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.state = self.STATE_MAIN

        elif self.state == self.STATE_HELP:
            if self._btn_back.is_clicked(event):
                self.state = self.STATE_MAIN

    def _start_game(self):
        from scenes.gameplay_scene import Gameplay_Scene
        cls, name, _, _ = self.CHARACTERS[self.selected_idx]
        player = cls(x=640, y=360)
        self.game.player = player
        self.game.change_scene(Gameplay_Scene(self.game, player))

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((18, 18, 22))
        if self.state == self.STATE_MAIN:
            self._draw_main(screen)
        elif self.state == self.STATE_CHARACTER:
            self._draw_character(screen)
        elif self.state == self.STATE_HELP:
            self._draw_help(screen)

    # ---- helpers ---- #

    def _draw_title(self, screen):
        title = self._font_title.render("DEADZONE", True, (200, 30, 30))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 110)))

    def _draw_main(self, screen):
        self._draw_title(screen)
        sw = screen.get_width()

        # Personnage sélectionné
        _, name, _, key = self.CHARACTERS[self.selected_idx]
        portrait = self._portraits.get(key)
        if portrait:
            # Miniature 48x48 à gauche du texte
            mini = pygame.transform.scale(portrait, (48, 48))
            px = sw // 2 - 130
            py = 165
            screen.blit(mini, (px, py))
            sub = self._font_sub.render(f"Perso : {name}", True, (160, 200, 255))
            screen.blit(sub, (px + 56, py + 12))
        else:
            sub = self._font_sub.render(f"Perso : {name}", True, (160, 200, 255))
            screen.blit(sub, sub.get_rect(center=(sw // 2, 182)))

        self._btn_play.draw(screen, self._font_btn)
        self._btn_char.draw(screen, self._font_btn)
        self._btn_help.draw(screen, self._font_btn)
        self._btn_quit.draw(screen, self._font_btn)

    def _draw_character(self, screen):
        self._draw_title(screen)
        sw, sh = screen.get_size()
        cx = sw // 2

        cls, name, desc, key = self.CHARACTERS[self.selected_idx]

        # Portrait central
        portrait = self._portraits.get(key)
        if portrait:
            big = pygame.transform.scale(portrait, (160, 160))
            screen.blit(big, big.get_rect(center=(cx, sh // 2 - 20)))
        else:
            # Fallback carré coloré
            colors = [(100, 150, 255), (100, 220, 150), (220, 150, 100)]
            col = colors[self.selected_idx % len(colors)]
            pygame.draw.rect(screen, col, (cx - 64, sh//2 - 84, 128, 128), border_radius=12)

        # Nom
        n_surf = self._font_title.render(name, True, (255, 255, 255))
        screen.blit(n_surf, n_surf.get_rect(center=(cx, sh // 2 - 140)))

        # Description pouvoir
        d_surf = self._font_sub.render(desc, True, (100, 220, 255))
        screen.blit(d_surf, d_surf.get_rect(center=(cx, sh // 2 + 110)))

        # Indicateur pagination
        dots = ""
        for i in range(len(self.CHARACTERS)):
            dots += "● " if i == self.selected_idx else "○ "
        dot_surf = self._font_sub.render(dots.strip(), True, (180, 180, 180))
        screen.blit(dot_surf, dot_surf.get_rect(center=(cx, sh // 2 + 145)))

        # Boutons
        self._btn_prev.draw(screen, self._font_btn)
        self._btn_next.draw(screen, self._font_btn)
        self._btn_select.draw(screen, self._font_btn)
        self._btn_back.draw(screen, self._font_btn)

        # Hint clavier
        hint = self._font_info.render("Fleches gauche/droite pour naviguer", True, (100, 100, 100))
        screen.blit(hint, hint.get_rect(center=(cx, sh - 30)))

    def _draw_help(self, screen):
        self._draw_title(screen)
        sw = screen.get_width()

        lines = [
            ("Deplacement",         "Z / Q / S / D"),
            ("Tirer",               "Clic gauche"),
            ("Inventaire",          "TAB"),
            ("Ramasser objet",      "E"),
            ("Pouvoir special",     "P"),
            ("Retour au menu",      "Echap"),
        ]

        y = 210
        for label, key in lines:
            l_surf = self._font_sub.render(label, True, (200, 200, 200))
            k_surf = self._font_sub.render(key,   True, (100, 200, 255))
            screen.blit(l_surf, (sw // 2 - 280, y))
            screen.blit(k_surf, (sw // 2 + 40,  y))
            y += 40

        self._btn_back.draw(screen, self._font_btn)
