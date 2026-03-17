import pygame, copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

BG_CHECK_A = ( 58,  52,  72)
BG_CHECK_B = ( 48,  44,  62)
LEATHER    = ( 62,  42,  28)
LEATHER_L  = ( 90,  62,  38)
PARCH      = (208, 192, 152)
PARCH_D    = (185, 168, 124)
PARCH_L    = (228, 215, 180)
SEAM       = (140, 118,  80)
SLOT_BG    = (158, 142, 102)
SLOT_BG_H  = (188, 172, 135)
SLOT_IN    = (138, 122,  88)
INK        = ( 28,  22,  14)
INK_D      = ( 80,  68,  48)
GOLD       = (195, 158,  42)
GOLD_L     = (225, 192,  70)
RED_INK    = (160,  40,  30)
RIVET      = ( 72,  78,  88)
RIVET_L    = (110, 118, 130)

RARITY_COL = {
    "commun":        (100, 100, 100),
    "rare":          ( 40, 100, 195),
    "epique":        (120,  35, 190),
    "\u00e9pique":   (120,  35, 190),
    "legendaire":    (185, 120,  18),
    "l\u00e9gendaire": (185, 120,  18),
}

def _rivet(surf, cx, cy, r=5):
    pygame.draw.circle(surf, RIVET,   (cx, cy), r)
    pygame.draw.circle(surf, RIVET_L, (cx, cy), r-1)
    pygame.draw.circle(surf, RIVET,   (cx, cy), r-2)

def _leather_panel(surf, x, y, w, h):
    pygame.draw.rect(surf, LEATHER,   (x,   y,   w,   h))
    pygame.draw.rect(surf, LEATHER_L, (x+2, y+2, w-4, h-4), 2)
    pygame.draw.rect(surf, PARCH,     (x+6, y+6, w-12, h-12))
    for cx, cy in [(x+8,y+8),(x+w-9,y+8),(x+8,y+h-9),(x+w-9,y+h-9)]:
        _rivet(surf, cx, cy)

def _draw_slot(surf, x, y, sz, hover=False, rarity=None):
    bg = SLOT_BG_H if hover else SLOT_BG
    pygame.draw.rect(surf, bg,      (x,   y,   sz,  sz))
    pygame.draw.rect(surf, SLOT_IN, (x,   y,   sz,   2))
    pygame.draw.rect(surf, SLOT_IN, (x,   y,    2,  sz))
    pygame.draw.rect(surf, PARCH_L, (x,   y+sz-2, sz, 2))
    pygame.draw.rect(surf, PARCH_L, (x+sz-2, y,   2,  sz))
    if rarity:
        rc = RARITY_COL.get(rarity, SLOT_IN)
        pygame.draw.rect(surf, rc, (x, y, 3, sz))
        pygame.draw.rect(surf, rc, (x, y, sz, 3))

class ChestScene:

    SLOT   = 48
    MARGIN = 5
    COLS   = 4         

    def __init__(self, game, player, chest, return_scene=None):
        self.game         = game
        self.player       = player
        self.chest        = chest
        self.return_scene = return_scene

        sw = game.screen.get_width()
        sh = game.screen.get_height()

        pw, ph = 780, 520
        px = (sw - pw) // 2
        py = (sh - ph) // 2
        self.panel = (px, py, pw, ph)

        
        half_w = pw // 2 - 20
        grid_h = 280
        self.chest_rect = (px + 10, py + 40, half_w, grid_h)
        self.inv_rect   = (px + pw // 2 + 10, py + 40, half_w, grid_h)

        self.chest_gx = px + 10 + 12
        self.chest_gy = py + 40 + 28

        self.inv_gx = px + pw // 2 + 10 + 12
        self.inv_gy = py + 40 + 28

       
        desc_y         = py + 40 + grid_h + 10
        desc_h         = 100
        self.desc_rect = (px + 10, desc_y, pw - 20, desc_h)

        self.F = {
            "title": pygame.font.Font(None, 34),
            "sec":   pygame.font.Font(None, 20),
            "item":  pygame.font.Font(None, 19),
            "hint":  pygame.font.Font(None, 17),
            "qty":   pygame.font.Font(None, 20),
        }

        self.hovered_chest_item = None
        self.hovered_inv_item   = None

        self._load_images()
        self._bg = self._build_bg(sw, sh)

    
    def _build_bg(self, sw, sh):
        s = pygame.Surface((sw, sh))
        for i in range(0, sw, 24):
            for j in range(0, sh, 24):
                c = BG_CHECK_A if (i//24 + j//24) % 2 == 0 else BG_CHECK_B
                pygame.draw.rect(s, c, (i, j, 24, 24))


        vg = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for r in range(0, max(sw, sh)//2, 3):
            a = max(0, int(80 * (1 - r / (max(sw, sh) / 2))))
            pygame.draw.circle(vg, (0, 0, 0, a), (sw//2, sh//2), r, 4)
        s.blit(vg, (0, 0))

        px, py, pw, ph = self.panel
        _leather_panel(s, px, py, pw, ph)


        mid = px + pw // 2
        pygame.draw.line(s, LEATHER, (mid, py + 20), (mid, py + ph - 20), 3)

        return s


    def _load_images(self):
        sz = self.SLOT - 8
        all_items = list(self.chest.items) + list(self.player.inventory.items)
        base = Path(__file__).parent.parent
        for item in all_items:
            if item.image_surface is None:
                try:
                    surf = pygame.image.load(str(base / "assets" / "items" / item.illustration)).convert_alpha()
                    item.image_surface = pygame.transform.scale(surf, (sz, sz))
                except Exception:
                    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
                    s.fill(SLOT_IN)
                    t = pygame.font.Font(None, 30).render("?", True, INK_D)
                    s.blit(t, t.get_rect(center=(sz//2, sz//2)))
                    item.image_surface = s


    def _slot_pos(self, i, grid_x, grid_y):
        col = i % self.COLS
        row = i // self.COLS
        return (grid_x + col * (self.SLOT + self.MARGIN),
                grid_y + row * (self.SLOT + self.MARGIN))


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_e):
                self._close()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._click(event.pos)

    def _close(self):
        if self.return_scene:
            self.game.change_scene(self.return_scene)
        else:
            from scenes.gameplay_scene import Gameplay_Scene
            self.game.change_scene(Gameplay_Scene(self.game, self.player))

    def _click(self, pos):
        mx, my = pos

        for i, item in enumerate(list(self.chest.items)):
            x, y = self._slot_pos(i, self.chest_gx, self.chest_gy)
            if pygame.Rect(x, y, self.SLOT, self.SLOT).collidepoint(mx, my):
                if self.player.inventory.add_item(item):
                    self.chest.take_item(item)
                    self._load_images()


        for i, item in enumerate(list(self.player.inventory.items)):
            x, y = self._slot_pos(i, self.inv_gx, self.inv_gy)
            if pygame.Rect(x, y, self.SLOT, self.SLOT).collidepoint(mx, my):
                chest_item = copy.copy(item)          
                self.player.inventory.remove_item(item, quantity=item.quantity)
                self.chest.items.append(chest_item)   
                self._load_images()
                return

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.hovered_chest_item = None
        self.hovered_inv_item   = None

        for i, item in enumerate(self.chest.items):
            x, y = self._slot_pos(i, self.chest_gx, self.chest_gy)
            if pygame.Rect(x, y, self.SLOT, self.SLOT).collidepoint(mx, my):
                self.hovered_chest_item = item
                break

        for i, item in enumerate(self.player.inventory.items):
            x, y = self._slot_pos(i, self.inv_gx, self.inv_gy)
            if pygame.Rect(x, y, self.SLOT, self.SLOT).collidepoint(mx, my):
                self.hovered_inv_item = item
                break

    def draw(self, screen):
        screen.blit(self._bg, (0, 0))
        px, py, pw, ph = self.panel
        F=self.F

        t=F["title"].render("COFFRE",True,GOLD_L)
        ts=F["title"].render("COFFRE",True,(60,40,20))
        tx = px + pw//2 - t.get_width()//2
        screen.blit(ts,(tx+1,py+9)); screen.blit(t,(tx,py+8))


        self._panel_title(screen, "Contenu du coffre", *self.chest_rect[:2], self.chest_rect[2])
        self._panel_title(screen, "Votre inventaire",  *self.inv_rect[:2],   self.inv_rect[2])

        self._draw_grid(screen, self.chest.items,            self.chest_gx, self.chest_gy, self.hovered_chest_item)
        self._draw_grid(screen, self.player.inventory.items, self.inv_gx,   self.inv_gy,   self.hovered_inv_item)

        if not self.chest.items:
            empty = self.F["sec"].render("(coffre vide)", True, INK_D)
            screen.blit(empty, (self.chest_gx, self.chest_gy))

 
        self._draw_desc(screen)
 

        hints = [
            ("Clic  Prendre",    (55, 160, 55)),
            ("Clic droit  Déposer", (190, 100, 15)),
            ("[E / Échap]  Fermer",  INK_D),
        ]
        Fh  = pygame.font.Font(None, 17)
        pad = 8
        gap = 10
        total_w = sum(Fh.size(h)[0] + pad*2 + gap for h, _ in hints) - gap
        hx = px + pw//2 - total_w//2
        hy = py + ph - 22
        for ht, hc in hints:
            tw, th = Fh.size(ht)
            bg = pygame.Surface((tw + pad*2, th + 6), pygame.SRCALPHA)
            bg.fill((20, 16, 10, 190))
            screen.blit(bg, (hx, hy - 3))
            pygame.draw.rect(screen, hc, (hx, hy-3, tw + pad*2, th+6), 1)
            screen.blit(Fh.render(ht, True, hc), (hx + pad, hy))
            hx += tw + pad*2 + gap

    def _draw_desc(self, screen):
        item = self.hovered_chest_item or self.hovered_inv_item
        dx, dy, dw, dh = self.desc_rect


        pygame.draw.rect(screen, PARCH_D, (dx, dy, dw, dh))
        pygame.draw.rect(screen, LEATHER, (dx, dy, dw, dh), 2)
        self._panel_title(screen, "Description", dx, dy - 12, dw)

        if not item:
            t = self.F["hint"].render("Survole un objet...", True, INK_D)
            screen.blit(t, (dx + 10, dy + dh // 2 - 8))
            return

        ix, iy = dx + 8, dy + 8
        sz = 40
        if item.image_surface:
            ic = pygame.transform.scale(item.image_surface, (sz, sz))
            screen.blit(ic, (ix, iy))

        rc = RARITY_COL.get(item.rarity, INK)
        screen.blit(self.F["sec"].render(item.name, True, rc), (ix + sz + 10, iy))
        screen.blit(self.F["hint"].render(f"[{item.rarity.upper()}]  {item.category.capitalize()}", True, rc), (ix + sz + 10, iy + 18))

        words = item.description.split()
        lines, line = [], []
        for w in words:
            line.append(w)
            if self.F["item"].size(" ".join(line))[0] > dw - sz - 30:
                lines.append(" ".join(line[:-1]))
                line = [w]
        if line:
            lines.append(" ".join(line))
        for i, l in enumerate(lines[:2]):
            screen.blit(self.F["item"].render(l, True, INK), (ix + sz + 10, iy + 36 + i * 15))

        if item.effect:
            screen.blit(self.F["hint"].render(f"Effet : +{item.effect}", True, INK_D), (ix + sz + 10, iy + 66))

    def _panel_title(self, screen, text, rx, ry, rw):
        F   = self.F["sec"]
        t   = F.render(text, True, RED_INK)
        tw  = t.get_width() + 20
        th  = t.get_height() + 6
        tx  = rx + rw//2 - tw//2
        pygame.draw.rect(screen, LEATHER,   (tx, ry + 1, tw, th))
        pygame.draw.rect(screen, LEATHER_L, (tx+1, ry+2, tw-2, th-2), 1)
        screen.blit(t, (tx + 10, ry + 4))

    def _draw_grid(self, screen, items, gx, gy, hovered):
        for i, item in enumerate(items):
            x, y   = self._slot_pos(i, gx, gy)
            is_hov = item is hovered
            _draw_slot(screen, x, y, self.SLOT, hover=is_hov, rarity=item.rarity)

            if item.image_surface:
                ox = (self.SLOT - item.image_surface.get_width())  // 2
                oy = (self.SLOT - item.image_surface.get_height()) // 2
                screen.blit(item.image_surface, (x + ox, y + oy))

            if item.quantity > 1:
                qt  = self.F["qty"].render(str(item.quantity), True, (190, 50, 30))
                qx  = x + self.SLOT - qt.get_width()  - 2
                qy  = y + self.SLOT - qt.get_height() - 1
                bg  = pygame.Surface((qt.get_width()+4, qt.get_height()+2), pygame.SRCALPHA)
                bg.fill((208, 192, 152, 200))
                screen.blit(bg, (qx-2, qy-1))
                screen.blit(qt, (qx, qy))

            if is_hov:
                hl = pygame.Surface((self.SLOT, self.SLOT), pygame.SRCALPHA)
                hl.fill((255, 255, 220, 40))
                screen.blit(hl, (x, y))