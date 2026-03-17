import pygame, sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from systems.crafting_manager import CraftingManager
from scenes.craft_scene import CraftScene

BG_CHECK_A = ( 58,  52,  72)
BG_CHECK_B = ( 48,  44,  62)
LEATHER = ( 62,  42,  28)
LEATHER_L = ( 90,  62,  38)
PARCH = (208, 192, 152)
PARCH_D = (185, 168, 124)
PARCH_L = (228, 215, 180)
SEAM = (140, 118,  80)
SLOT_BG = (158, 142, 102)
SLOT_BG_H = (188, 172, 135)
SLOT_IN = (138, 122,  88)
SLOT_EQ = (142, 150, 130)
INK = ( 28,  22,  14)
INK_D = ( 80,  68,  48)
GOLD = (195, 158,  42)
GOLD_L = (225, 192,  70)
RED_INK = (160,  40,  30)
RIVET = ( 72,  78,  88)
RIVET_L = (110, 118, 130)

RARITY_COL = {
    "commun": (100, 100, 100),
    "rare": ( 40, 100, 195),
    "epique": (120,  35, 190),
    "legendaire": (185, 120,  18),
}
SLOT_LABELS = {"helmet":"Casque","chestplate":"Plastron","boots":"Bottes","weapon":"Arme"}

def rivet(surf, cx, cy, r=5):
    pygame.draw.circle(surf, RIVET, (cx, cy), r)
    pygame.draw.circle(surf, RIVET_L, (cx, cy), r-1)
    pygame.draw.circle(surf, RIVET, (cx, cy), r-2)

def leather_panel(surf, x, y, w, h):
    pygame.draw.rect(surf, LEATHER, (x,   y,   w,   h))
    pygame.draw.rect(surf, LEATHER_L,(x+2, y+2, w-4, h-4), 2)
    pygame.draw.rect(surf, PARCH, (x+6, y+6, w-12,h-12))

    rng = random.Random(x*31+y)
    for _ in range((w-12)*(h-12)//25):
        px = rng.randint(x+6, x+w-7)
        py2= rng.randint(y+6, y+h-7)
        v = rng.randint(-12, 8)
        cf = PARCH
        surf.set_at((px,py2),(max(0,min(255,cf[0]+v)),
                              max(0,min(255,cf[1]+v)),
                              max(0,min(255,cf[2]+v))))

    for cx2, cy2 in [(x+8,y+8),(x+w-9,y+8),(x+8,y+h-9),(x+w-9,y+h-9)]:
        rivet(surf, cx2, cy2)

def panel_title(surf, text, rx, ry, rw, font, col=RED_INK):
    t = font.render(text, True, col)
    tw = t.get_width() + 20
    th = t.get_height() + 6
    tx = rx + rw//2 - tw//2
    pygame.draw.rect(surf, LEATHER,  (tx, ry+1, tw, th))
    pygame.draw.rect(surf, LEATHER_L,(tx+1,ry+2, tw-2, th-2), 1)
    surf.blit(t, (tx+10, ry+4))

    pygame.draw.rect(surf, GOLD, (tx, ry+th//2, 6, 2))
    pygame.draw.rect(surf, GOLD, (tx+tw-6, ry+th//2, 6, 2))

def draw_slot(surf, x, y, sz, hover=False, rarity=None, eq=False):
    bg = SLOT_EQ if eq else (SLOT_BG_H if hover else SLOT_BG)
    pygame.draw.rect(surf, bg, (x, y, sz, sz))
    pygame.draw.rect(surf, SLOT_IN,(x, y, sz, 2))
    pygame.draw.rect(surf, SLOT_IN,(x, y, 2, sz))
    pygame.draw.rect(surf, PARCH_L,(x, y+sz-2, sz, 2))
    pygame.draw.rect(surf, PARCH_L,(x+sz-2, y, 2, sz))
    if rarity:
        rc = RARITY_COL.get(rarity, SLOT_IN)
        pygame.draw.rect(surf, rc, (x, y, 3, sz))
        pygame.draw.rect(surf, rc, (x, y, sz, 3))

def draw_char_silhouette(surf, cx, cy):
    S = (120, 112, 88)

    pygame.draw.ellipse(surf, S, (cx-13, cy-74, 26, 26))

    pygame.draw.rect(surf, S, (cx-16, cy-50, 32, 40))

    pygame.draw.rect(surf, S, (cx-28, cy-48, 12, 30))
    pygame.draw.rect(surf, S, (cx+16, cy-48, 12, 30))

    pygame.draw.rect(surf, S, (cx-15, cy-12, 13, 34))
    pygame.draw.rect(surf, S, (cx+2, cy-12, 13, 34))

def stitch_line(surf, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1
    n = max(abs(dx),abs(dy))
    if n==0: return
    for i in range(0, n, 8):
        t = i/n
        t2= min(1,(i+4)/n)
        ax,ay = int(x1+t*dx), int(y1+t*dy)
        bx,by = int(x1+t2*dx), int(y1+t2*dy)
        pygame.draw.line(surf, SEAM, (ax,ay),(bx,by),1)

class InventoryScene:
    SLOT=48; MARGIN=5; COLS=7

    def __init__(self, game, player, return_scene=None):
        self.game=game; self.player=player; self.return_scene=return_scene
        sw=game.screen.get_width(); sh=game.screen.get_height()

        pw,ph = 900, 580
        px = (sw-pw)//2
        py = (sh-ph)//2
        self.panel=(px,py,pw,ph)

        lw = self.COLS*(self.SLOT+self.MARGIN)-self.MARGIN+26
        lh = 3*(self.SLOT+self.MARGIN)-self.MARGIN+26
        self.left=(px+14, py+30, lw, lh)
        self.gx = px+14+13; self.gy = py+30+22

        dh=118
        self.desc=(px+14, py+30+lh+10, lw, dh)

        rsx = px+14+lw+14; rsy = py+16
        rsw = pw-(rsx-px)-14; rsh = ph-32
        self.right=(rsx,rsy,rsw,rsh)

        self.ccx = rsx+rsw//2
        self.ccy = rsy+rsh//2-10

        esz=self.SLOT+6
        self.equipment_positions={
            "helmet": (self.ccx-esz*2-14, self.ccy-80),
            "chestplate": (self.ccx-esz*2-14, self.ccy-20),
            "boots": (self.ccx-esz*2-14, self.ccy+40),
            "weapon": (self.ccx+esz+14,   self.ccy-50),
        }
        self.equipment_slot_size=esz

        self.F={"title": pygame.font.Font(None,38),
                "sec": pygame.font.Font(None,21),
                "item": pygame.font.Font(None,19),
                "hint": pygame.font.Font(None,17),
                "qty": pygame.font.Font(None,20)}

        self.hovered_item=None; self.hovered_slot=None; self.desc_item=None
        self.crafting_manager=CraftingManager(self.player.inventory)
        self.craf_scene=CraftScene(self.game,self.crafting_manager)
        self._load_item_images()
        self._bg=self._build_bg(sw,sh)

    def _build_bg(self,sw,sh):
        s=pygame.Surface((sw,sh))
        for i in range(0,sw,24):
            for j in range(0,sh,24):
                c=BG_CHECK_A if (i//24+j//24)%2==0 else BG_CHECK_B
                pygame.draw.rect(s,c,(i,j,24,24))

        vg=pygame.Surface((sw,sh),pygame.SRCALPHA)
        for r in range(0,max(sw,sh)//2,3):
            a=max(0,int(80*(1-r/(max(sw,sh)/2))))
            pygame.draw.circle(vg,(0,0,0,a),(sw//2,sh//2),r,4)
        s.blit(vg,(0,0))

        px,py,pw,ph=self.panel
        leather_panel(s,px,py,pw,ph)

        stitch_line(s, px+18, py+20, px+pw-18, py+20)
        stitch_line(s, px+18, py+ph-20, px+pw-18, py+ph-20)

        mx = px+14+self.left[2]+14
        stitch_line(s, mx+6, py+20, mx+6, py+ph-20)
        pygame.draw.line(s, LEATHER, (mx+7, py+20),(mx+7, py+ph-20),2)
        return s

    def _load_item_images(self):
        sz=self.SLOT-8
        all_items=list(self.player.inventory.items)
        for v in self.player.equipment.values():
            if v and v not in all_items: all_items.append(v)
        for item in all_items:
            if item.image_surface is None:
                try:
                    _base=Path(__file__).parent.parent
                    _img_path=_base/"assets"/"items"/item.illustration
                    surf=pygame.image.load(str(_img_path)).convert_alpha()
                    item.image_surface=pygame.transform.scale(surf,(sz,sz))
                except:
                    s=pygame.Surface((sz,sz),pygame.SRCALPHA); s.fill(SLOT_IN)
                    t=pygame.font.Font(None,30).render("?",True,INK_D)
                    s.blit(t,t.get_rect(center=(sz//2,sz//2)))
                    item.image_surface=s

    def handle_event(self,event):
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_TAB):
                if self.return_scene: self.game.change_scene(self.return_scene)
                else:
                    from scenes.gameplay_scene import Gameplay_Scene
                    self.game.change_scene(Gameplay_Scene(self.game,self.player))
            elif event.key==pygame.K_e and self.hovered_item:
                for sn,eq in self.player.equipment.items():
                    if eq is self.hovered_item:
                        self.player.unequip_item(sn); self._load_item_images(); return
                self._equip_hovered_item()
            elif event.key==pygame.K_c: self.craf_scene.toggle()
        if event.type==pygame.MOUSEBUTTONDOWN:
            if event.button==1: self._click(event.pos)
            if event.button==3: self._rclick(event.pos)
        self.craf_scene.handle_event(event)

    def _equip_hovered_item(self):
        item=self.hovered_item
        if not item: return
        if item.category=="arme": self.player.equip_item(item,"weapon")
        elif item.category=="armure":
            n=item.name.lower()
            if "casque" in n or "helmet" in n: self.player.equip_item(item,"helmet")
            elif "plastron" in n or "chestplate" in n: self.player.equip_item(item,"chestplate")
            elif "botte" in n or "boots" in n: self.player.equip_item(item,"boots")
        self._load_item_images()

    def _slot_pos(self,i):
        col=i%self.COLS; row=i//self.COLS
        return (self.gx+col*(self.SLOT+self.MARGIN), self.gy+row*(self.SLOT+self.MARGIN))

    def _click(self,pos):
        mx,my=pos
        for sn,(sx,sy) in self.equipment_positions.items():
            if pygame.Rect(sx,sy,self.equipment_slot_size,self.equipment_slot_size).collidepoint(mx,my):
                if self.player.equipment[sn]: self.player.unequip_item(sn); self._load_item_images()
                return
        for i,item in enumerate(self.player.inventory.items):
            x,y=self._slot_pos(i)
            if pygame.Rect(x,y,self.SLOT,self.SLOT).collidepoint(mx,my):
                if item.category in ("soin","nourriture","boisson"):
                    self.player.use_item(item); self._load_item_images()
                break

    def _rclick(self,pos):
        mx,my=pos
        for i,item in enumerate(self.player.inventory.items):
            x,y=self._slot_pos(i)
            if pygame.Rect(x,y,self.SLOT,self.SLOT).collidepoint(mx,my):
                self.player.inventory.remove_item(item,quantity=1); self._load_item_images(); break

    def update(self,dt):
        mx,my=pygame.mouse.get_pos()
        self.hovered_item=self.hovered_slot=self.desc_item=None
        for sn,(sx,sy) in self.equipment_positions.items():
            if pygame.Rect(sx,sy,self.equipment_slot_size,self.equipment_slot_size).collidepoint(mx,my):
                self.hovered_slot=sn
                if self.player.equipment[sn]:
                    self.hovered_item=self.desc_item=self.player.equipment[sn]
                return
        for i,item in enumerate(self.player.inventory.items):
            x,y=self._slot_pos(i)
            if pygame.Rect(x,y,self.SLOT,self.SLOT).collidepoint(mx,my):
                self.hovered_item=self.desc_item=item; break

    def draw(self,screen):
        screen.blit(self._bg,(0,0))
        px,py,pw,ph=self.panel
        F=self.F

        t=F["title"].render("INVENTAIRE",True,GOLD_L)
        ts=F["title"].render("INVENTAIRE",True,(60,40,20))
        tx=px+pw//2-t.get_width()//2
        screen.blit(ts,(tx+1,py+9)); screen.blit(t,(tx,py+8))

        for ox in (tx-8, tx+t.get_width()+2):
            pygame.draw.rect(screen,GOLD,(ox,py+14,6,2))

        lx,ly,lw,lh=self.left
        panel_title(screen,"Sac à dos",lx,ly-12,lw,F["sec"],RED_INK)
        self._draw_grid(screen)

        dx,dy,dw,dh=self.desc
        panel_title(screen,"Description",dx,dy-12,dw,F["sec"],RED_INK)
        self._draw_desc(screen)

        rx,ry,rw,rh=self.right
        panel_title(screen,"Equipement",rx,ry-12,rw,F["sec"],RED_INK)

        sx2=self.ccx-60; sy2=self.ccy-82
        pygame.draw.rect(screen,PARCH_D,(sx2,sy2,120,168))
        pygame.draw.rect(screen,SLOT_IN,(sx2,sy2,120,168),1)
        draw_char_silhouette(screen,self.ccx,self.ccy)

        self._draw_eq_slots(screen)
        self._draw_stats(screen)

        hints=[("[E] Équiper",(55,160,55)),("[C] Craft",(190,100,15)),
               ("Clic Droit  Jeter",(190,45,30)),("[TAB] Fermer",INK_D)]
        Fh=pygame.font.Font(None,19); pad=9; gap=12
        total_hw=sum(Fh.size(h)[0]+pad*2+gap for h,_ in hints)-gap
        hx2=px+pw//2-total_hw//2; hy2=py+ph-24
        for ht,hc in hints:
            tw2,th2=Fh.size(ht)
            bg2=pygame.Surface((tw2+pad*2,th2+6),pygame.SRCALPHA)
            bg2.fill((20,16,10,190)); screen.blit(bg2,(hx2,hy2-3))
            pygame.draw.rect(screen,hc,(hx2,hy2-3,tw2+pad*2,th2+6),1)
            screen.blit(Fh.render(ht,True,hc),(hx2+pad,hy2))
            hx2+=tw2+pad*2+gap

        self.craf_scene.draw(screen)

    def _draw_grid(self,screen):
        for i in range(self.COLS*3):
            x,y=self._slot_pos(i)
            item=self.player.inventory.items[i] if i<len(self.player.inventory.items) else None
            hover=item is not None and item is self.hovered_item
            draw_slot(screen,x,y,self.SLOT,hover=hover,rarity=item.rarity if item else None)
            if not item: continue
            if item.image_surface:
                ox=(self.SLOT-item.image_surface.get_width())//2
                oy=(self.SLOT-item.image_surface.get_height())//2
                screen.blit(item.image_surface,(x+ox,y+oy))
            if item.quantity>1:
                qt=self.F["qty"].render(str(item.quantity),True,(190,50,30))
                qx=x+self.SLOT-qt.get_width()-2; qy=y+self.SLOT-qt.get_height()-1
                bg=pygame.Surface((qt.get_width()+4,qt.get_height()+2),pygame.SRCALPHA)
                bg.fill((208,192,152,200)); screen.blit(bg,(qx-2,qy-1)); screen.blit(qt,(qx,qy))
            if item.durability<100:
                dw2=int((self.SLOT-4)*item.durability/100)
                dc=(50,175,50) if item.durability>50 else (195,130,25) if item.durability>25 else (185,35,35)
                pygame.draw.rect(screen,SLOT_IN,(x+2,y+self.SLOT-5,self.SLOT-4,3))
                pygame.draw.rect(screen,dc,(x+2,y+self.SLOT-5,dw2,3))
            if hover:
                hl=pygame.Surface((self.SLOT,self.SLOT),pygame.SRCALPHA)
                hl.fill((255,255,220,30)); screen.blit(hl,(x,y))

    def _draw_desc(self,screen):
        dx,dy,dw,dh=self.desc
        ix,iy=dx+8,dy+8
        item=self.desc_item
        if not item:
            t=self.F["hint"].render("Survole un objet...",True,INK_D)
            screen.blit(t,(ix,iy+dh//2-8)); return
        sz=40
        if item.image_surface:
            ic=pygame.transform.scale(item.image_surface,(sz,sz))
            screen.blit(ic,(ix,iy+2))
        rc=RARITY_COL.get(item.rarity,INK)
        nt=self.F["sec"].render(item.name,True,rc)
        screen.blit(nt,(ix+sz+8,iy+2))
        rt=self.F["hint"].render(f"[{item.rarity.upper()}]  {item.category.capitalize()}",True,rc)
        screen.blit(rt,(ix+sz+8,iy+20))

        words=item.description.split(); lines2=[]; line2=[]
        for w in words:
            line2.append(w)
            if self.F["item"].size(" ".join(line2))[0]>dw-sz-28:
                lines2.append(" ".join(line2[:-1])); line2=[w]
        if line2: lines2.append(" ".join(line2))
        for li,l in enumerate(lines2[:3]):
            screen.blit(self.F["item"].render(l,True,INK),(ix+sz+8,iy+38+li*15))
        sy3=iy+dh-20
        pygame.draw.line(screen,SEAM,(ix,sy3-4),(ix+dw-16,sy3-4),1)
        sl=f"Durabilite: {item.durability}%   Qte: {item.quantity}"
        if item.effect: sl+=f"   Effet: +{item.effect}"
        screen.blit(self.F["hint"].render(sl,True,INK_D),(ix,sy3))

    def _draw_eq_slots(self,screen):
        for sn,(sx,sy) in self.equipment_positions.items():
            sz=self.equipment_slot_size; eq=self.player.equipment[sn]
            hover=self.hovered_slot==sn
            draw_slot(screen,sx,sy,sz,hover=hover,eq=True,
                      rarity=eq.rarity if eq else None)
            lbl=self.F["hint"].render(SLOT_LABELS[sn],True,INK_D)
            screen.blit(lbl,(sx+sz//2-lbl.get_width()//2,sy-15))
            if eq and eq.image_surface:
                osz=sz-8
                ic=pygame.transform.scale(eq.image_surface,(osz,osz))
                screen.blit(ic,(sx+(sz-osz)//2,sy+(sz-osz)//2))
            else:
                g={"helmet":"C","chestplate":"P","boots":"B","weapon":"A"}.get(sn,"?")
                gt=self.F["sec"].render(g,True,SLOT_IN)
                screen.blit(gt,(sx+sz//2-gt.get_width()//2,sy+sz//2-gt.get_height()//2))
            if hover and eq:
                hl=pygame.Surface((sz,sz),pygame.SRCALPHA)
                hl.fill((255,255,220,35)); screen.blit(hl,(sx,sy))

    def _draw_stats(self,screen):
        rx,ry,rw,rh=self.right
        p=self.player

        bw = 140
        bx = self.ccx - bw//2

        nb = 4 if p.max_shield>0 else 3
        total_h = nb*30
        by = ry + rh - total_h - 14
        Fbar  = pygame.font.Font(None, 18)
        Fval  = pygame.font.Font(None, 17)

        def bar(label,val,maxv,col,yo):
            lbl=Fbar.render(label,True,INK_D)
            screen.blit(lbl,(bx, by+yo))
            bar_y = by+yo+13
            bar_h = 9
            fw=int(bw*max(0,min(1,val/maxv))) if maxv>0 else 0

            pygame.draw.rect(screen,SLOT_IN,(bx, bar_y, bw, bar_h))

            if fw>0: pygame.draw.rect(screen,col,(bx, bar_y, fw, bar_h))

            pygame.draw.rect(screen,SEAM,(bx, bar_y, bw, bar_h),1)

            txt=f"{int(val)}/{int(maxv)}"
            vsurf=Fval.render(txt,True,INK_D)
            screen.blit(vsurf,(bx+bw+6, bar_y + bar_h//2 - vsurf.get_height()//2))

        bar("Vie",      p.health, p.max_health, (175,45,45),   0)
        bar("Soif",     p.thirst, p.max_thirst, (45,115,175),  30)
        bar("Faim",     p.hunger, p.max_hunger, (155,125,35),  60)
        if p.max_shield>0:
            bar("Bouclier",p.shield,p.max_shield,(45,125,195), 90)