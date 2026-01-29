import pickle

class Items:
    def __init__(self, name, durability, category, rarity, illustration, quantity=1):
        self._name = name 
        self._durability = durability
        self._category = category
        self._rarity = rarity
        self._quantity = quantity
        self._illustration = illustration
    
    def __str__(self):
        return (f"{self._name} \n| Durabilité : {self._durability} \n| Catégorie : {self._category} \n| Rareté : {self._rarity} \n| Quantité : {self._quantity}\n")
    
    def to_dict_item(self):
        return {
            'name': self._name,
            'durability': self._durability,
            'category': self._category,
            'rarity': self._rarity,
            'quantity': self._quantity
        }

    def is_same_item(self, other):
        return(self._name == other._name and self._category == other._category and self._rarity == other._rarity)
    
class Inventory:
    def __init__(self):
        self._inventory = []

    def __str__(self):
        if not self._inventory:
            return "Inventaire Vide"

        texte = "\n Inventaire du joueur :\n"
        for item in self._inventory:
            texte += f"• {item}\n"
        return texte     
    
    def add_item(self, name, durability, category, rarity, illustration, quantity=1,):

        new_item = Items(name, durability, category, rarity, illustration, quantity)

        for item in self._inventory:
            if item.is_same_item(new_item):
                item._quantity += 1
                print(f"• {name} x {quantity} ajouté (Total: {item._quantity})")
                return
        
        self._inventory.append(new_item)
        print(f"• Nouveau {name} ajouté")
    
    def drop_item(self, name, durability, category, rarity, illustration, quantity=1):

        drop_item = Items(name, durability, category, rarity, illustration, quantity)

        for item in self._inventory:
            if item.is_same_item(drop_item):
                item._quantity -= 1
                if item._quantity <= 0:
                    self._inventory.remove(item)
                print(f"• {name} x {quantity} supprimé (Total: {item._quantity})")
                return

if __name__ == "__main__": 
  
    player = Inventory()
    player.add_item("Fusil à pompe", 100, "arme", "rare", "shotgun.png")
    player.add_item("Fusil à pompe", 100, "arme", "rare", "shotgun.png")
    player.add_item("Bouclier", 30, "Armure", "épique", "shield.png")
    player.add_item("Fusil à pompe", 100, "arme", "rare", "shotgun.png")
    player.add_item("Soin", 1, "soin", "légendaire", "potion_legendary.png")
    player.add_item("Bouclier", 30, "Armure", "épique", "shield.png")
    player.add_item("Soin", 1, "soin", "légendaire", "potion_legendary.png")
    player.add_item("Soin", 1, "soin", "légendaire", "potion_legendary.png")

    player.drop_item("Soin", 1, "soin", "légendaire", "potion_legendary.png")
    player.drop_item("Soin", 1, "soin", "légendaire", "potion_legendary.png")
    
    print(player)

