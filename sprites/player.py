import pygame
import os

class Player(pygame.sprite.Sprite):

    def __init__(self, x ,y):
        super().__init__()
        base_dir = os.path.dirname(os.path.abspath(__file__))  # dossier sprites/
        asset_dir = os.path.join(base_dir, "..", "asset")  # remonte d'un niveau puis va dans asset/
        self.sprite_sheet = pygame.image.load(os.path.join(asset_dir, "player.png"))
        self.image = self.get_image( 0, 0) 
        self.image.set_colorkey([0, 0, 0])
        self.rect = self.image.get_rect()
        self.position = [x, y]
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 12)
        self.old_position = self.position.copy()
        self.speed = 3

    def save_location(self): self.old_position = self.position.copy()


    def move_right(self): self.position[0] += self.speed
    def move_left(self): self.position[0] -= self.speed
    def move_up(self): self.position[1] -= self.speed
    def move_down(self): self.position[1] += self.speed

    def update(self):
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    
    def get_image(self, x, y):  
        image = pygame.Surface([16, 16])
        image.blit(self.sprite_sheet, (0,0), (x, y, 32, 32))
        return image