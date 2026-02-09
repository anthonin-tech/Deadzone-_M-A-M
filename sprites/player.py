import pygame
import time

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
    
class Mahe(Character):
    def __init__(self):
        super().__init__("Mahé", hp=20, attack=12, defense=3)

        self.power_active = False
        self.cooldown = False
        self.start_time = 0

        self.DURATION = 60
        self.COOLDOWN = 60

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


class Maelys(Character):
    def __init__(self):
        super().__init__("Maëlys", hp=30, attack=8, defense=5)

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


class Anthonin(Character):
    def __init__(self):
        super().__init__("Anthonin", hp=14, attack=9, defense=2)

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


# =========================
# 🧪 TEST TERMINAL
# =========================
if __name__ == "__main__":
    mahe = Mahe()
    maelys = Maelys()
    anthonin = Anthonin()

    print(mahe)
    print(maelys)
    print(anthonin)

    mahe.activate_power()
    maelys.activate_power()
    anthonin.activate_power()

    while True:
        mahe.update_power()
        maelys.update_power()
        anthonin.update_power()
        time.sleep(1)

