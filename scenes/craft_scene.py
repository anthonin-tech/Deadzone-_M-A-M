import pygame, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from systems.crafting_manager import CraftingManager
from sprites.recipes import RECIPES

IRON      = ( 38,  40,  50)
IRON_L    = ( 62,  66,  80)
IRON_HL   = ( 90,  95, 115)
PARCH     = (205, 188, 148)
PARCH_D   = (178, 162, 122)
INK       = ( 28,  22,  14)
INK_D     = ( 88,  74,  52)
GOLD      = (190, 155,  38)
GOLD_L    = (222, 188,  68)
EMBER     = (195,  80,  28)
EMBER_L   = (230, 120,  45)
GREEN_OK  = ( 52, 135,  62)
GREEN_OKL = ( 78, 175,  90)
RED_NO    = (135,  38,  38)
SEAM      = (140, 118,  80)

def _rivet(surf, cx, cy):
    pygame.draw.circle(surf, (55,60,72), (cx,cy), 5)
    pygame.draw.circle(surf, (95,102,120),(cx,cy), 3)
    pygame.draw.circle(surf, (55,60,72), (cx,cy), 1)

def _forge_panel(surf, x, y, w, h):
    pygame.draw.rect(surf, (22,24,30),   (x,   y,   w,   h))
    pygame.draw.rect(surf, IRON_L,       (x+2, y+2, w-4, h-4), 2)
    pygame.draw.rect(surf, IRON_HL,      (x+3, y+3, w-6, 2))
    pygame.draw.rect(surf, PARCH,        (x+6, y+6, w-12,h-12))
    for cx,cy in [(x+8,y+8),(x+w-9,y+8),(x+8,y+h-9),(x+w-9,y+h-9)]:
        _rivet(surf, cx, cy)

def _ingredient_tag(surf, text, x, y, available, font):
    col  = GREEN_OKL if available else RED_NO
    bg   = (28,52,32) if available else (52,24,24)
    t    = font.render(text, True, col)
    tw   = t.get_width()+10
    th   = t.get_height()+4
    pygame.draw.rect(surf, bg,       (x, y, tw, th))
    pygame.draw.rect(surf, col,      (x, y, tw, th), 1)
    surf.blit(t, (x+5, y+2))
    return tw+4

class CraftScene:
    def __init__(self, game, crafting_manager: CraftingManager):
        self.game = game
        self.cm   = crafting_manager
        self.visible = False
        self.hovered_recipe = None
        self.scroll = 0
        self.selected = None
        self._anim  = {}
        self._crafted_since_last_poll = False

        sw, sh = game.screen.get_width(), game.screen.get_height()
        pw, ph = 460, 560
        self.rect = pygame.Rect(sw-pw-18, (sh-ph)//2, pw, ph)
        self.list_y0 = self.rect.y + 56
        self.ROW_H   = 80
        self.clip_rect = pygame.Rect(
            self.rect.x+6, self.list_y0,
            self.rect.w-12, self.rect.h-56-14)

        self.F = {
            "title": pygame.font.Font(None, 34),
            "name":  pygame.font.Font(None, 24),
            "info":  pygame.font.Font(None, 19),
            "hint":  pygame.font.Font(None, 18),
            "tag":   pygame.font.Font(None, 17),
        }
        self._panel_surf = None

    def _build_panel_surf(self):
        s = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        _forge_panel(s, 0, 0, self.rect.w, self.rect.h)

        pygame.draw.rect(s, IRON,   (6, 6, self.rect.w-12, 42))
        pygame.draw.rect(s, IRON_HL,(6, 6, self.rect.w-12, 2))
        pygame.draw.rect(s, IRON_L, (6, 6, self.rect.w-12, 42), 1)

        hx, hy = 16, 14
        pygame.draw.rect(s, GOLD_L, (hx,   hy,   10, 6))
        pygame.draw.rect(s, GOLD,   (hx+2, hy+6, 4, 14))
        pygame.draw.rect(s, IRON_HL,(hx,   hy,   10, 2))

        t = self.F["title"].render("ATELIER", True, GOLD_L)
        ts= self.F["title"].render("ATELIER", True, (40,28,10))
        s.blit(ts, (32, 13)); s.blit(t, (31, 12))

        sub = self.F["hint"].render("Clic pour fabriquer", True, INK_D)
        s.blit(sub, (self.rect.w - sub.get_width() - 14, 22))

        pygame.draw.rect(s, IRON_L, (6, 48, self.rect.w-12, 2))
        pygame.draw.rect(s, IRON_HL,(6, 49, self.rect.w-12, 1))
        self._panel_surf = s

    def toggle(self):
        self.visible = not self.visible
        self.scroll  = 0
        self.selected = None
        if self.visible and self._panel_surf is None:
            self._build_panel_surf()

    def poll_crafted(self):
        crafted = self._crafted_since_last_poll
        self._crafted_since_last_poll = False
        return crafted

    def handle_event(self, event):
        if not self.visible: return
        if event.type == pygame.MOUSEMOTION:
            self.hovered_recipe = self._recipe_at(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            recipe = self._recipe_at(event.pos)
            if recipe:
                if self.cm.can_craft(recipe):
                    self.cm.craft(recipe)
                    self._anim[recipe["id"]] = pygame.time.get_ticks()
                    self._crafted_since_last_poll = True
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                max_scroll = max(0, len(RECIPES)*self.ROW_H - self.clip_rect.h)
                self.scroll = max(0, min(max_scroll, self.scroll - event.y*20))

    def _recipe_at(self, pos):
        if not self.clip_rect.collidepoint(pos): return None
        rel_y = pos[1] - self.list_y0 + self.scroll
        idx   = int(rel_y // self.ROW_H)
        return RECIPES[idx] if 0 <= idx < len(RECIPES) else None

    def draw(self, screen):
        if not self.visible: return
        now = pygame.time.get_ticks()

        screen.blit(self._panel_surf, (self.rect.x, self.rect.y))

        screen.set_clip(self.clip_rect)

        for i, recipe in enumerate(RECIPES):
            y = self.list_y0 + i*self.ROW_H - self.scroll
            if y+self.ROW_H < self.clip_rect.y or y > self.clip_rect.bottom:
                continue

            rx = self.rect.x + 8
            rw = self.rect.w - 16
            can     = self.cm.can_craft(recipe)
            hover   = recipe is self.hovered_recipe
            flash_t = self._anim.get(recipe["id"], 0)
            flashing= (now - flash_t) < 400

            if flashing:
                alpha = max(0, 255 - int((now-flash_t)*255/400))
                row_bg = (30, int(90*(alpha/255)), 30)
            elif hover and can:
                row_bg = (35, 52, 35)
            elif can:
                row_bg = (28, 40, 30)
            elif hover:
                row_bg = (50, 32, 32)
            else:
                row_bg = (24, 26, 32)

            pygame.draw.rect(screen, row_bg,  (rx, y+2, rw, self.ROW_H-4))
            pygame.draw.rect(screen, IRON_L,  (rx, y+2, rw, self.ROW_H-4), 1)

            bar_c = GREEN_OK if can else RED_NO
            pygame.draw.rect(screen, bar_c, (rx, y+2, 4, self.ROW_H-4))

            result = recipe["result"]
            ico_x, ico_y, ico_sz = rx+10, y+8, 48
            pygame.draw.rect(screen, PARCH_D, (ico_x, ico_y, ico_sz, ico_sz))
            pygame.draw.rect(screen, SEAM,    (ico_x, ico_y, ico_sz, ico_sz), 1)

            img = self._get_result_img(result, ico_sz-6)
            if img:
                ox=(ico_sz-img.get_width())//2; oy=(ico_sz-img.get_height())//2
                screen.blit(img, (ico_x+ox, ico_y+oy))

            if result.quantity > 1:                                
               qt = self.F["tag"].render(f"x{result.quantity}", True, GOLD_L)

            tx = ico_x + ico_sz + 10
            nc = GOLD_L if can else (100,90,70)
            nt = self.F["name"].render(result.name, True, nc)
            screen.blit(nt, (tx, y+8))

            tag_x = tx; tag_y = y+32
            for ing_name, ing_qty in recipe["ingredients"].items():

                inv_qty = sum(it.quantity for it in self.cm.inventory.items if it.name==ing_name)
                ok = inv_qty >= ing_qty
                label = f"{ing_name} {inv_qty}/{ing_qty}"
                adv = _ingredient_tag(screen, label, tag_x, tag_y, ok, self.F["tag"])
                tag_x += adv
                if tag_x > rx+rw-60:
                    tag_x = tx; tag_y += 20

            if hover and can:
                ht = self.F["hint"].render("Cliquer pour fabriquer", True, GREEN_OKL)
                screen.blit(ht, (rx+rw-ht.get_width()-10, y+self.ROW_H-22))

            if flashing:
                alpha = max(0, int((now-flash_t)*200/400))
                fls = pygame.Surface((rw, self.ROW_H-4), pygame.SRCALPHA)
                fls.fill((60,200,60,alpha))
                screen.blit(fls, (rx, y+2))
                ok_t = self.F["name"].render("Fabriqué !", True, GREEN_OKL)
                screen.blit(ok_t, (rx+rw//2-ok_t.get_width()//2, y+self.ROW_H//2-8))

        screen.set_clip(None)

        total_h = len(RECIPES)*self.ROW_H
        if total_h > self.clip_rect.h:
            sb_h  = int(self.clip_rect.h * self.clip_rect.h / total_h)
            sb_y  = self.clip_rect.y + int(self.scroll * self.clip_rect.h / total_h)
            sb_x  = self.rect.right - 10
            pygame.draw.rect(screen, IRON_L, (sb_x, self.clip_rect.y, 4, self.clip_rect.h))
            pygame.draw.rect(screen, GOLD,   (sb_x, sb_y, 4, sb_h))

        cx = self.rect.right - 22; cy = self.rect.y + 14
        pygame.draw.rect(screen, IRON,   (cx-10, cy-8, 20, 16))
        pygame.draw.rect(screen, IRON_HL,(cx-10, cy-8, 20, 16), 1)
        xt = self.F["hint"].render("✕", True, (180,80,60))
        screen.blit(xt, (cx-xt.get_width()//2, cy-xt.get_height()//2))

    _img_cache = {}
    def _get_result_img(self, result, sz):
        key = (result.illustration, sz)  
        if key in self._img_cache: return self._img_cache[key]
        try:
            surf = pygame.image.load(str(Path(__file__).parent.parent / "assets_items" / "items" / result.illustration)).convert_alpha()
            surf = pygame.transform.scale(surf, (sz, sz))
            self._img_cache[key] = surf
        except:
            self._img_cache[key] = None
        return self._img_cache[key]
