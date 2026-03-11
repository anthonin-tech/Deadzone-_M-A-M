import pygame, sys, random, math
from pathlib import Path
from sprites.projectile import Projectile
sys.path.insert(0, str(Path(__file__).parent.parent))

Z_SKIN   = (100, 140,  90)
Z_SKIN_S = ( 70, 100,  62)
Z_BODY   = ( 62,  88, 105)
Z_BODY_S = ( 42,  62,  78)
Z_PANTS  = ( 48,  52,  68)
Z_BOOT   = ( 32,  34,  44)
Z_HAIR   = ( 28,  30,  38)
Z_TEETH  = (220, 210, 185)
Z_EYE    = (210,  30,  30)
Z_BLOOD  = (150,  15,  15)
Z_OUT    = ( 18,  18,  22)

def _s(w=16,h=20): return pygame.Surface((w,h),pygame.SRCALPHA)
def _r(s,c,x,y,w,h): pygame.draw.rect(s,c,(x,y,w,h))
def _hit(s):
    o=pygame.Surface(s.get_size(),pygame.SRCALPHA); o.fill((255,60,60,140)); s.blit(o,(0,0))

def _outline(s, col=Z_OUT):
    w,h=s.get_size()
    o=pygame.Surface((w,h),pygame.SRCALPHA)
    alpha=pygame.surfarray.pixels_alpha(s)
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        for x in range(w):
            for y in range(h):
                if alpha[x,y]>128:
                    nx,ny=x+dx,y+dy
                    if 0<=nx<w and 0<=ny<h and alpha[nx,ny]<10:
                        o.set_at((nx,ny),(*col,255))
    del alpha
    res=pygame.Surface((w,h),pygame.SRCALPHA)
    res.blit(o,(0,0)); res.blit(s,(0,0))
    return res

class ZombieAnim:

    @staticmethod
    def normal(frame=0, hit=False, atk=False):
        s=_s(16,22)

        _r(s,Z_HAIR,  4,0, 8,3)
        _r(s,Z_HAIR,  3,1, 2,2); _r(s,Z_HAIR,11,1,2,2)

        _r(s,Z_SKIN,  3,2,10,7)
        _r(s,Z_SKIN_S,3,2, 1,7); _r(s,Z_SKIN_S,12,2,1,7)

        _r(s,Z_EYE,   5,4, 2,2); _r(s,Z_EYE,9,4,2,2)
        _r(s,Z_OUT,   6,4, 1,1); _r(s,Z_OUT,10,4,1,1)

        _r(s,Z_BLOOD, 7,6, 4,1)

        _r(s,Z_OUT,   5,8, 6,1)
        _r(s,Z_TEETH, 6,8, 1,1); _r(s,Z_TEETH,8,8,1,1); _r(s,Z_TEETH,10,8,1,1)

        _r(s,Z_BODY,  4,9, 8,6)
        _r(s,Z_BODY_S,4,9, 1,6); _r(s,Z_BODY_S,11,9,1,6)
        _r(s,Z_OUT,   5,9, 1,1); _r(s,Z_OUT,10,9,1,1)

        _r(s,(200,185,155),6,10,4,1); _r(s,(200,185,155),5,11,4,1)

        if atk:
            _r(s,Z_BODY, 0,8,4,3); _r(s,Z_BODY,12,8,4,3)
            _r(s,Z_SKIN, 0,10,4,2); _r(s,Z_SKIN,12,10,4,2)
            _r(s,Z_BLOOD,0,11,2,1); _r(s,Z_BLOOD,14,11,2,1)
        else:
            aw = 1 if frame==1 else 0
            _r(s,Z_BODY, 1,9+aw,3,5); _r(s,Z_BODY,12,9-aw,3,5)
            _r(s,Z_SKIN, 1,13+aw,3,2); _r(s,Z_SKIN,12,13-aw,3,2)

        if frame==0 or atk:
            _r(s,Z_PANTS,5,15,3,3); _r(s,Z_PANTS,8,15,3,3)
            _r(s,Z_BOOT, 5,18,3,2); _r(s,Z_BOOT, 8,18,3,2)
        else:
            _r(s,Z_PANTS,4,15,3,4); _r(s,Z_PANTS,9,14,3,3)
            _r(s,Z_BOOT, 4,19,3,2); _r(s,Z_BOOT, 9,17,3,2)
        if hit: _hit(s)
        return s

    @staticmethod
    def fast(frame=0, hit=False, atk=False):
        s=_s(14,22)
        EYE_F=(220,180,20)
        SHIRT=(95,75,45)

        _r(s,Z_HAIR, 4,0,6,3)
        _r(s,Z_SKIN, 3,2,8,6)
        _r(s,EYE_F,  4,4,2,2); _r(s,EYE_F,8,4,2,2)
        _r(s,Z_OUT,  5,4,1,1); _r(s,Z_OUT,9,4,1,1)
        _r(s,Z_BLOOD,5,7,4,1)
        _r(s,Z_OUT,  4,8,6,1)

        _r(s,SHIRT,  4,8,6,6)
        _r(s,Z_BODY_S,4,8,1,6); _r(s,Z_BODY_S,9,8,1,6)

        f3=frame%3
        if atk:
            _r(s,Z_SKIN,0,7,4,3); _r(s,Z_SKIN,10,7,4,3)
            _r(s,Z_BLOOD,3,9,1,1); _r(s,Z_BLOOD,10,9,1,1)
        else:
            offt=(0,2,1)[f3]
            _r(s,SHIRT,  1,8+offt,3,5); _r(s,SHIRT, 10,8-offt,3,5)
            _r(s,Z_SKIN, 1,12+offt,3,2); _r(s,Z_SKIN,10,12-offt,3,2)

        if f3==0:
            _r(s,Z_PANTS,4,14,2,4); _r(s,Z_PANTS,8,14,2,4)
            _r(s,Z_BOOT, 4,18,2,3); _r(s,Z_BOOT, 8,18,2,3)
        elif f3==1:
            _r(s,Z_PANTS,3,13,2,5); _r(s,Z_PANTS,9,15,2,3)
            _r(s,Z_BOOT, 3,18,2,3); _r(s,Z_BOOT, 9,18,2,3)
        else:
            _r(s,Z_PANTS,4,14,2,4); _r(s,Z_PANTS,8,13,2,5)
            _r(s,Z_BOOT, 4,18,2,3); _r(s,Z_BOOT, 8,18,2,3)
        if hit: _hit(s)
        return s

    @staticmethod
    def tank(frame=0, hit=False, atk=False):
        s=_s(22,24)
        ARMOR=(50,60,80); ARMOR_S=(35,45,62)

        _r(s,Z_HAIR, 4,0,14,4)
        _r(s,Z_SKIN, 3,3,16,8)
        _r(s,Z_SKIN_S,3,3,1,8); _r(s,Z_SKIN_S,18,3,1,8)
        _r(s,Z_EYE,  5,5,3,2); _r(s,Z_EYE,14,5,3,2)
        _r(s,Z_OUT,  6,5,1,1); _r(s,Z_OUT,15,5,1,1)

        _r(s,Z_BLOOD,10,4,1,5); _r(s,Z_BLOOD,8,6,2,1)

        _r(s,Z_OUT,  7,9,8,2)
        _r(s,Z_TEETH,8,9,2,1); _r(s,Z_TEETH,11,9,2,1)

        _r(s,ARMOR,  2,11,18,8)
        _r(s,ARMOR_S,2,11,1,8); _r(s,ARMOR_S,19,11,1,8)
        _r(s,(70,80,100),4,11,14,1)
        _r(s,(70,80,100),4,14,14,1)
        _r(s,Z_OUT,  7,12,1,2); _r(s,Z_OUT,14,12,1,2)

        ay=10 if atk else 12
        _r(s,ARMOR,  0,ay,2,7); _r(s,ARMOR,20,ay,2,7)
        _r(s,Z_SKIN, 0,ay+6,2,3); _r(s,Z_SKIN,20,ay+6,2,3)

        if frame==0:
            _r(s,Z_PANTS,4,19,6,4); _r(s,Z_PANTS,12,19,6,4)
            _r(s,Z_BOOT, 4,22,6,2); _r(s,Z_BOOT, 12,22,6,2)
        else:
            _r(s,Z_PANTS,3,19,6,4); _r(s,Z_PANTS,13,18,6,4)
            _r(s,Z_BOOT, 3,22,6,2); _r(s,Z_BOOT, 13,21,6,2)
        if hit: _hit(s)
        return s

    @staticmethod
    def boss(frame=0, hit=False, atk=False, phase=1):
        s=_s(22,26)

        if phase==1:
            ROBE=(38,28,58); EYE_C=(170,20,240); TRIM=(90,60,130)
        elif phase==2:
            ROBE=(55,18,78); EYE_C=(210,50,255); TRIM=(130,50,180)
        else:
            ROBE=(80,10,25); EYE_C=(255,40, 40); TRIM=(190,30, 60)
        CROWN=(200,165,25); CROWN_S=(140,115,10)

        if phase>=2:
            ac=(*TRIM[:3],40)
            for r in [11,9,7]:
                asurf=pygame.Surface((22,26),pygame.SRCALPHA)
                pygame.draw.ellipse(asurf,ac,(11-r,13-r,r*2,r*2))
                s.blit(asurf,(0,0))

        _r(s,CROWN_S,4,2,14,1)
        _r(s,CROWN,  4,0,14,3)
        for cx in (4,8,12,16):
            _r(s,CROWN,cx,0,2,5)
        _r(s,(230,200,50),4,2,14,1)

        _r(s,Z_SKIN_S,3,4,16,9)
        _r(s,Z_SKIN,  4,5,14,7)

        _r(s,EYE_C,   5,6,3,2); _r(s,EYE_C,14,6,3,2)
        _r(s,(255,255,255,200),5,6,1,1); _r(s,(255,255,255,200),14,6,1,1)
        _r(s,Z_OUT,   6,6,1,1); _r(s,Z_OUT,15,6,1,1)

        _r(s,Z_BLOOD, 9,5,1,5); _r(s,Z_BLOOD,7,8,3,1)

        _r(s,ROBE,    3,13,16,9)
        _r(s,Z_OUT,   3,13,1,9); _r(s,Z_OUT,18,13,1,9)
        _r(s,TRIM,    3,13,16,2)
        _r(s,TRIM,    3,18,16,1)
        _r(s,Z_OUT,   7,14,1,2); _r(s,Z_OUT,14,14,1,2)

        _r(s,Z_OUT,   2,15,1,7); _r(s,Z_OUT,19,15,1,7)

        ay=11 if atk else 13
        _r(s,ROBE,    0,ay,3,7); _r(s,ROBE,19,ay,3,7)
        _r(s,TRIM,    0,ay,3,2); _r(s,TRIM,19,ay,3,2)
        _r(s,Z_SKIN,  0,ay+6,3,2); _r(s,Z_SKIN,19,ay+6,3,2)

        if frame==0:
            _r(s,ROBE,4,22,6,3); _r(s,ROBE,12,22,6,3)
            _r(s,Z_BOOT,4,24,6,2); _r(s,Z_BOOT,12,24,6,2)
        else:
            _r(s,ROBE,3,22,6,3); _r(s,ROBE,13,21,6,3)
            _r(s,Z_BOOT,3,24,6,2); _r(s,Z_BOOT,13,23,6,2)
        if hit: _hit(s)
        return s

class Enemy:
    WALK_FPS=6; IDLE_FPS=1.5; SPRITE_W=16; SPRITE_H=22

    def __init__(self,x,y):
        self.x=x; self.y=y
        self.speed=45; self.radius=6
        self.health=30; self.max_health=30
        self.detection_radius=150; self.attack_distance=14
        self.damage=6; self.attack_cooldown=1400; self.last_attack=0
        self._frame=0; self._timer=0.0
        self._moving=False; self._atk=False
        self._hit=False; self._hit_t=0.0; self._flip=False
        self._cache={}

    def _get_player_pos(self,p):
        return (p.position.x,p.position.y) if hasattr(p,"position") else (p.x,p.y)

    def calculate_distance(self,tx,ty):
        return math.sqrt((tx-self.x)**2+(ty-self.y)**2)

    def move_towards(self,tx,ty,dt):
        d=self.calculate_distance(tx,ty)
        if d>0:
            self.x+=(tx-self.x)/d*self.speed*dt
            self.y+=(ty-self.y)/d*self.speed*dt
            self._moving=True
            if (tx-self.x)<0: self._flip=True
            elif (tx-self.x)>0: self._flip=False

    def can_attack(self):
        return pygame.time.get_ticks()-self.last_attack>=self.attack_cooldown

    def attack(self,player):
        if self.can_attack():
            player.take_damage(self.damage,self.x,self.y)
            self.last_attack=pygame.time.get_ticks()
            self._atk=True

    def take_hit(self):
        self._hit=True; self._hit_t=0.15

    def update(self,dt,player,enemies=None,projectiles=None):
        if player is None:
            self._moving=self._atk=False
            if self._hit:
                self._hit_t-=dt
                if self._hit_t<=0: self._hit=False
            return
        px,py=self._get_player_pos(player)
        dist=self.calculate_distance(px,py)
        self._moving=self._atk=False
        if dist<=self.attack_distance:
            self.attack(player); self._atk=True
        elif dist<=self.detection_radius:
            self.move_towards(px,py,dt)
        if self._hit:
            self._hit_t-=dt
            if self._hit_t<=0: self._hit=False
        fps=self.WALK_FPS if self._moving else self.IDLE_FPS
        self._timer+=dt
        if self._timer>=1.0/fps:
            self._timer=0.0
            self._frame=(self._frame+1)%3

    def _get_raw(self):
        return ZombieAnim.normal(self._frame%2, self._hit, self._atk)

    def _get_scaled(self, zoom):
        key=(self._frame%2, self._hit, self._atk, zoom)
        if key not in self._cache:
            raw=self._get_raw()
            sw,sh=raw.get_size()
            sc=pygame.transform.scale(raw,(int(sw*zoom),int(sh*zoom)))
            self._cache[key]=sc
            if len(self._cache)>24: self._cache.pop(next(iter(self._cache)))
        return self._cache[key]

    def draw(self,screen,sx=None,sy=None,zoom=3):
        dx=sx if sx is not None else int(self.x)
        dy=sy if sy is not None else int(self.y)
        sc=self._get_scaled(zoom)
        if self._flip: sc=pygame.transform.flip(sc,True,False)
        dw,dh=sc.get_size()
        screen.blit(sc,(dx-dw//2,dy-dh//2))
        self._draw_hp(screen,dx,dy,dh)

    def _draw_hp(self,screen,dx,dy,sprite_h):
        bw=max(38,sprite_h); bh=5
        bx=dx-bw//2; by=dy-sprite_h//2-14
        r=max(0,self.health)/self.max_health
        fw=int(bw*r)
        col=(55,200,55) if r>0.5 else (210,140,30) if r>0.25 else (200,35,35)
        pygame.draw.rect(screen,(20,20,20),(bx,by,bw,bh))
        pygame.draw.rect(screen,col,(bx,by,fw,bh))
        pygame.draw.rect(screen,(80,80,80),(bx,by,bw,bh),1)
        f=pygame.font.Font(None,14)
        t=f.render(f"{max(0,int(self.health))}/{int(self.max_health)}",True,(210,200,185))
        screen.blit(t,t.get_rect(center=(dx,by-7)))

class FastEnemy(Enemy):
    WALK_FPS=10; SPRITE_W=14; SPRITE_H=22
    def __init__(self,x,y):
        super().__init__(x,y)
        self.speed=70
        self.health=20
        self.max_health=20
        self.damage=5
        self.attack_cooldown=1200
    def _get_raw(self):
        return ZombieAnim.fast(self._frame%3, self._hit, self._atk)

class TankEnemy(Enemy):
    WALK_FPS=3; SPRITE_W=22; SPRITE_H=24
    def __init__(self,x,y):
        super().__init__(x,y)
        self.speed=28
        self.health=150
        self.max_health=150
        self.damage=12
        self.attack_cooldown=2000
        self.radius=9

    def _get_raw(self):
        return ZombieAnim.tank(self._frame%2, self._hit, self._atk)

class BossEnemy(Enemy):
    IDLE="idle"
    CHASE="chase"
    CASTING="casting"
    RECOVERY="recovery"
    WALK_FPS=4
    SPRITE_W=22
    SPRITE_H=26

    def __init__(self,x,y):
        super().__init__(x,y)
        self.speed=32; self.health=280; self.max_health=280
        self.damage=10; self.radius=12
        self.state=self.IDLE; self.phase=1
        self.cast_skill=None; self.cast_end=0; self.rec_end=0
        self.last_special=0; self.global_cd=6000
        self.skill_order=["projectile","aoe","summon"]; self.skill_idx=0
        self.skills={
            "aoe":        {"cd":10000,"last":-99999,"cast":900, "rec":800, "pmin":1},
            "summon":     {"cd":18000,"last":-99999,"cast":1300,"rec":1000,"pmin":2},
            "projectile": {"cd":5000, "last":-99999,"cast":600, "rec":500, "pmin":1},
        }

    def _get_raw(self):
        return ZombieAnim.boss(self._frame%2, self._hit,
            self._atk or self.state==self.CASTING, self.phase)

    def _phase_update(self):
        r=self.health/self.max_health
        self.phase=3 if r<=0.4 else 2 if r<=0.7 else 1

    def _pick_skill(self,now):
        for i in range(len(self.skill_order)):
            idx=(self.skill_idx+i)%len(self.skill_order)
            n=self.skill_order[idx]; d=self.skills[n]
            if (now-d["last"])>=d["cd"] and self.phase>=d["pmin"]:
                self.skill_idx=(idx+1)%len(self.skill_order); return n
        return None

    def _begin_cast(self,sk,now):
        self.state=self.CASTING; self.cast_skill=sk
        self.cast_end=now+self.skills[sk]["cast"]

    def _do_aoe(self,player):
        if self.calculate_distance(*self._get_player_pos(player))<=120:
            player.take_damage(12 if self.phase<3 else 20,self.x,self.y)

    def _do_summon(self,enemies):
        for _ in range(2 if self.phase==2 else 3):
            enemies.append(Enemy(self.x+random.randint(-70,70),self.y+random.randint(-70,70)))
        for _ in range(1 if self.phase==2 else 2):
            enemies.append(FastEnemy(self.x+random.randint(-70,70),self.y+random.randint(-70,70)))

    def _do_proj(self,projs,player):
        px,py=(player.position.x,player.position.y) if hasattr(player,"position") else (player.x,player.y)
        shots=1 if self.phase<3 else 2
        base=math.atan2(py-self.y,px-self.x)
        for i in range(shots):
            a=base+(i-(shots-1)/2)*0.16
            projs.append(Projectile(self.x,self.y,
                pygame.Vector2(math.cos(a),math.sin(a)),
                speed=220,damage=8 if self.phase<3 else 14,
                radius=6,color=(40,40,40),max_distance=900,owner="enemy"))

    def _exec_cast(self,player,enemies,projs,now):
        sk=self.cast_skill
        if sk=="aoe": self._do_aoe(player)
        elif sk=="summon": self._do_summon(enemies)
        elif sk=="projectile": self._do_proj(projs,player)
        self.skills[sk]["last"]=now; self.last_special=now
        self.state=self.RECOVERY; self.rec_end=now+self.skills[sk]["rec"]
        self.cast_skill=None

    def update(self,dt,player,enemies=None,projectiles=None):
        if player is None:
            self._moving=self._atk=False
            if self._hit:
                self._hit_t-=dt
                if self._hit_t<=0: self._hit=False
            return
        now=pygame.time.get_ticks(); self._phase_update()
        self._moving=self._atk=False
        if self.state==self.CASTING:
            self._atk=True
            if now>=self.cast_end: self._exec_cast(player,enemies,projectiles,now)
        elif self.state==self.RECOVERY:
            if now>=self.rec_end: self.state=self.IDLE
        else:
            px,py=self._get_player_pos(player)
            dist=self.calculate_distance(px,py)
            self.state=self.CHASE if dist<=self.detection_radius else self.IDLE
            if self.state==self.CHASE and dist>self.attack_distance:
                self.move_towards(px,py,dt)
            elif dist<=self.attack_distance: self._atk=True
            if (now-self.last_special)>=self.global_cd:
                sk=self._pick_skill(now)
                if sk: self._begin_cast(sk,now)
        if self._hit:
            self._hit_t-=dt
            if self._hit_t<=0: self._hit=False
        fps=8 if self.state==self.CASTING else (self.WALK_FPS if self._moving else self.IDLE_FPS)
        self._timer+=dt
        if self._timer>=1.0/fps:
            self._timer=0.0; self._frame=(self._frame+1)%2

    def draw(self,screen,sx=None,sy=None,zoom=3):
        super().draw(screen,sx,sy,zoom)
        dx=sx if sx is not None else int(self.x)
        dy=sy if sy is not None else int(self.y)
        if self.state==self.CASTING and self.cast_skill=="aoe":
            pygame.draw.circle(screen,(255,80,80),(dx,dy),int(120*zoom),2)
