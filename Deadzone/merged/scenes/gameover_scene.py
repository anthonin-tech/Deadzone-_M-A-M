import pygame
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from sprites.player import Player
from scenes.gameplay_scene import Gameplay_Scene

class GameOverScene:
    def __init__(self, game, stats=None):
        self.game = game
        self.stats = stats or {}

        self.bg_color = (15, 15, 15)
        self.font_title = pygame.font.Font(None, 100)
        self.font_stat = pygame.font.Font(None, 36)
        self.font_button = pygame.font.Font(None, 40)

        self.alpha = 0
        self.fade_speed = 5
        self.title_scale = 0.5

        self.particles = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._restart_game()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def _restart_game(self):
        new_player = Player()
        self.game.change_scene(Gameplay_Scene(self.game, new_player))

    def update(self, dt):
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed)

        if self.title_scale < 1.0:
            self.title_scale = min(1.0, self.title_scale + 0.02)

    def draw(self, screen):
        screen.fill(self.bg_color)

        base_title = self.font_title.render("VOUS ÊTES MORT", True, (255, 0, 0))
        scaled_width = int(base_title.get_width() * self.title_scale)
        scaled_height = int(base_title.get_height() * self.title_scale)

        if scaled_width > 0 and scaled_height > 0:
            title = pygame.transform.scale(base_title, (scaled_width, scaled_height))
            title.set_alpha(self.alpha)
            title_rect = title.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 120))
            screen.blit(title, title_rect)

        if self.alpha >= 255:
            y = screen.get_height()//2 - 20

            if 'enemies_killed' in self.stats:
                stat_text = self.font_stat.render(
                    f"Enemi tué: {self.stats['enemies_killed']}",
                    True, (200, 200, 200)
                )
                stat_rect = stat_text.get_rect(center=(screen.get_width()//2, y))
                screen.blit(stat_text, stat_rect)
                y += 40

            if 'time_survived' in self.stats:
                stat_text = self.font_stat.render(
                    f"Temps survécu: {self.stats['time_survived']:.1f}s",
                    True, (200, 200, 200)
                )
                stat_rect = stat_text.get_rect(center=(screen.get_width()//2, y))
                screen.blit(stat_text, stat_rect)
                y += 60

                restart = self.font_button.render("[R] RECOMMENCER", True, (0, 255, 0))
                restart_rect = restart.get_rect(center=(screen.get_width()//2, y))
                screen.blit(restart, restart_rect)

                quit_text = self.font_button.render("[ESC] QUITTER", True, (255, 100, 100))
                quit_rect = quit_text.get_rect(center=(screen.get_width()//2, y + 50))
                screen.blit(quit_text, quit_rect)