import pygame
from pathlib import Path
from sprites.item import Items

class DroppedItem:
    def __init__(self, item, x, y):
        self.item = item
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.image = None
        self.pickup_radius = 50
        self.load_image()

        self.float_offset = 0
        self.float_speed = 2

    def load_image(self):
        try:
            img_path = Path("assets/items") / self.item.illustration
            self.image = pygame.image.load(str(img_path)).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((255, 200, 0))
            font = pygame.font.Font(None, 24)
            text = font.render("?", True, (0, 0, 0))
            text_rect = text.get_rect(center=(self.width//2, self.height//2))
            self.image.blit(text, text_rect)
        
    def get_rect(self):
        return pygame.Rect(self.x , self.y, self.width, self.height)
    
    def is_near(self, player_x, player_y):
        dx = self.x + self.width//2 - player_x
        dy = self.y + self.height//2 - player_y
        distance = (dx**2 + dy**2) ** 0.5
        return distance <= self.pickup_radius
    
    def update(self, dt):
        self.float_offset += self.float_speed * dt
        if self.float_offset > 10:
            self.float_speed = -abs(self.float_speed)
        elif self.float_offset < -10:
            self.float_speed = abs(self.float_speed)

    def draw(self, screen, camera_x=0, camera_y=0):
        if self.image:
            draw_y = self.y - camera_y + self.float_offset
            screen.blit(self.image, (self.x - camera_x, draw_y))

    