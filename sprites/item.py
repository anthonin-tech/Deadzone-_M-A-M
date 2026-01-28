import pickle

class Items:
    def __init__(self, name, durability, category, rarity, quantity=1):
        self._name = name 
        self._durability = durability
        self._category = category
        self._rarity = rarity
        self._quantity = quantity
        self._inventory = []

    def save(self):

        for key, value in self.__dict__.items():
            if key != "_inventory":
                self._inventory.append(value)

        print(self._inventory)

    
player_inventory = [Items("Fusil à pompe", 100, "arme", "rare"), Items("Soin", 1, "soin", "légendaire"), Items("Bouclier" , 30, "Armure", "épique")]

with open("save.pkl", "wb") as f:
    pickle.dump(player_inventory, f)

with open("save.pkl", "rb") as f:
    loaded_inventory = pickle.load(f)