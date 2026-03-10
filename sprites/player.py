import pygame
import time
from sprites.animation import AnimateSprite
class Character:
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense

    def __str__(self):
        return f"{self.name} | HP {self.hp}/{self.max_hp} | ATK {self.attack} | DEF {self.defense}"

    def take_damage(self, damage):
        real_damage = max(0, damage - self.defense)
        self.hp = max(0, self.hp - real_damage)
        return real_damage

class Mahé(AnimateSprite, Character):

    def __init__(self):
        AnimateSprite.__init__(self, sprite_column=0)
        Character.__init__(self, "Mahé", 20, 12, 3)

        self.rect = self.image.get_rect(center=(400, 300))
        self.position = [self.rect.x, self.rect.y]
        self.speed = 2

        self.power_active = False
        self.cooldown = False
        self.start_time = 0

        self.DURATION = 60
        self.COOLDOWN = 60

    def move_right(self):
        self.position[0] += self.speed
        self.change_animation("right")

    def move_left(self):
        self.position[0] -= self.speed
        self.change_animation("left")

    def move_up(self):
        self.position[1] -= self.speed
        self.change_animation("up")

    def move_down(self):
        self.position[1] += self.speed
        self.change_animation("down")

    def update(self):
        self.rect.topleft = self.position

    
    def activate_power(self):
        if self.power_active or self.cooldown:
            print("⏳ Uppercut indisponible.")
            return

        self.power_active = True
        self.start_time = time.time()
        print("🥊 UPPERCUT ACTIVÉ (+6 dégâts pendant 2 min)")

    def get_attack(self):
        if self.power_active:
            return self.attack + 6
        return self.attack

    def update_power(self):
        now = time.time()

        if self.power_active and now - self.start_time >= self.DURATION:
            self.power_active = False
            self.cooldown = True
            self.start_time = now
            print("⏳ Uppercut terminé. Recharge...")

        elif self.cooldown and now - self.start_time >= self.COOLDOWN:
            self.cooldown = False
            print("✅ Uppercut prêt !")

class Maelys(AnimateSprite, Character):

    def __init__(self):
        AnimateSprite.__init__(self, sprite_column=2)
        Character.__init__(self, "Maëlys", 30, 8, 5)

        self.rect = self.image.get_rect(center=(400, 300))
        self.position = [self.rect.x, self.rect.y]
        self.speed = 2

        self.shield_active = False
        self.cooldown = False
        self.start_time = 0

        self.DURATION = 60
        self.COOLDOWN = 60

    def activate_power(self):
        if self.shield_active or self.cooldown:
            print("⏳ Bouclier indisponible.")
            return

        self.shield_active = True
        self.start_time = time.time()
        print("🎾 BOUCLIER TENNIS ACTIVÉ (renvoi + réduction dégâts)")

    def take_damage(self, damage):
        if self.shield_active:
            reduced = damage // 2
            reflected = damage // 4
            self.hp -= max(0, reduced - self.defense)
            print(f"🎾 Maëlys renvoie {reflected} dégâts et réduit les dégâts !")
            return reflected

        return super().take_damage(damage)

    def update_power(self):
        now = time.time()

        if self.shield_active and now - self.start_time >= self.DURATION:
            self.shield_active = False
            self.cooldown = True
            self.start_time = now
            print("⏳ Bouclier terminé. Recharge...")

        elif self.cooldown and now - self.start_time >= self.COOLDOWN:
            self.cooldown = False
            print("✅ Bouclier prêt !")



    def move_right(self):
        self.position[0] += self.speed
        self.change_animation("right")

    def move_left(self):
        self.position[0] -= self.speed
        self.change_animation("left")

    def move_up(self):
        self.position[1] -= self.speed
        self.change_animation("up")

    def move_down(self):
        self.position[1] += self.speed
        self.change_animation("down")

    def update(self):
        self.rect.topleft = self.position


class Anthonin(AnimateSprite, Character):

    def __init__(self):
        AnimateSprite.__init__(self, sprite_column=1)
        Character.__init__(self, "Anthonin", 14, 9, 2)

        self.rect = self.image.get_rect(center=(400, 300))
        self.position = [self.rect.x, self.rect.y]
        self.speed = 2

        self.invisible = False
        self.cooldown = False
        self.start_time = 0

        self.DURATION = 60
        self.COOLDOWN = 60

        

    def activate_power(self):
        if self.invisible or self.cooldown:
            print("⏳ Pouvoir indisponible.")
            return

        self.invisible = True
        self.start_time = time.time()
        print("🧟 INVISIBLE AUX ZOMBIES (2 min)")

    def update_power(self):
        now = time.time()

        if self.invisible and now - self.start_time >= self.DURATION:
            self.invisible = False
            self.cooldown = True
            self.start_time = now
            print("⏳ Invisibilité terminée. Recharge...")

        elif self.cooldown and now - self.start_time >= self.COOLDOWN:
            self.cooldown = False
            print("✅ Invisibilité prête !")

    def move_right(self):
        self.position[0] += self.speed
        self.change_animation("right")

    def move_left(self):
        self.position[0] -= self.speed
        self.change_animation("left")

    def move_up(self):
        self.position[1] -= self.speed
        self.change_animation("up")

    def move_down(self):
        self.position[1] += self.speed
        self.change_animation("down")

    def update(self):
        self.rect.topleft = self.position



