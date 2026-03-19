import pygame
from pathlib import Path
from sprites.item import Items


_TILE_W = 16
_TILE_H = 16

_DISPLAY_W = _TILE_W * 3   
_DISPLAY_H = _TILE_H * 3   

_CLOSED_COL = 0
_OPEN_COL = 0
_ROW_CLOSED = 0
_ROW_OPEN = 1

_spritesheet: pygame.Surface | None = None

def _get_spritesheet() -> pygame.Surface:
    global _spritesheet
    if _spritesheet is None:
        path = Path(__file__).parent.parent / "asset_map" / "All_Chest_Sprites_Combined.png"
        _spritesheet = pygame.image.load(str(path)).convert_alpha()
    return _spritesheet

def _crop_tile(col: int, row: int) -> pygame.Surface:
    sheet = _get_spritesheet()
    tile  = pygame.Surface((_TILE_W, _TILE_H), pygame.SRCALPHA)
    tile.blit(sheet, (0, 0), (col * _TILE_W, row * _TILE_H, _TILE_W, _TILE_H))
    return pygame.transform.scale(tile, (_DISPLAY_W, _DISPLAY_H))


class Chest:

    INTERACT_DIST = 20

    def __init__(self, x: float, y: float, items=None):
        self.x = x
        self.y = y
        self.items = list(items) if items else []

        self.id = f"{self.x}_{self.y}"
        self.is_open = False

        self._surf_closed: pygame.Surface | None = None
        self._surf_open: pygame.Surface | None = None

    def _ensure_surfaces(self):
        if self._surf_closed is None:
            self._surf_closed = _crop_tile(_CLOSED_COL, _ROW_CLOSED)
            self._surf_open = _crop_tile(_OPEN_COL,   _ROW_OPEN)

    @property
    def width(self)  -> int: return _TILE_W
    @property
    def height(self) -> int: return _TILE_H

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), _TILE_W, _TILE_H)

    def is_near(self, player_x: float, player_y: float) -> bool:
        cx = self.x + _TILE_W / 2
        cy = self.y + _TILE_H / 2
        dx = cx - player_x
        dy = cy - player_y
        return (dx*dx + dy*dy) ** 0.5 <= self.INTERACT_DIST

    def open(self):
        self.is_open = True

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def take_item(self, item: Items):
        if item in self.items:
            self.items.remove(item)

    def draw(self, screen: pygame.Surface, sx: float, sy: float):
        self._ensure_surfaces()
        surf = self._surf_open if self.is_open else self._surf_closed
        screen.blit(surf, (int(sx), int(sy)))
