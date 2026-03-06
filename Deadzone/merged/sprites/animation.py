import pygame
import os

class AnimateSprite(pygame.sprite.Sprite):
    """
    Gère les animations directionnelles (haut/bas/gauche/droite)
    à partir d'une sprite sheet.
    Chaque personnage a une colonne différente dans la sprite sheet.
    """

    def __init__(self, sprite_column):
        super().__init__()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        asset_dir = os.path.join(base_dir, "..", "asset")
        sprite_path = os.path.join(asset_dir, "player_sheet.png")

        self.sprite_sheet = pygame.image.load(sprite_path).convert_alpha()

        self.animation_index = 0
        self.animation_speed = 0.15
        self.sprite_column = sprite_column

        self.images = {
            "down":  self.get_images(0),
            "left":  self.get_images(1),
            "right": self.get_images(2),
            "up":    self.get_images(3),
        }

        self.image = self.images["down"][0]
        self.rect = self.image.get_rect()

    def change_animation(self, direction):
        self.animation_index += self.animation_speed
        if self.animation_index >= len(self.images[direction]):
            self.animation_index = 0
        self.image = self.images[direction][int(self.animation_index)]

    def get_images(self, row):
        images = []
        for frame in range(3):
            x = (self.sprite_column * 3 + frame) * 16
            y = row * 16
            image = pygame.Surface((16, 16), pygame.SRCALPHA)
            image.blit(self.sprite_sheet, (0, 0), (x, y, 16, 16))
            image = pygame.transform.scale(image, (32, 32))
            images.append(image)
        return images
