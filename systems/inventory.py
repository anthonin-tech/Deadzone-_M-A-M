import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from sprites.item import Items

class Inventory:
    def __init__(self, capacity=20):
        self._inventory = []   
        self.capacity = capacity
    
    @property
    def items(self):
        return self._inventory
    
    def add_item(self, name, durability, category, rarity, illustration,  description, quantity=1):
        new_item = Items(name, durability, category, rarity, illustration,  description, quantity=1)

        for item in self._inventory:
            if item.is_same_item(new_item):
                item.quantity += quantity
                print(f"✅ {name} x{quantity} ajouté (Total: {item.quantity})")
                return True
        
        if len(self._inventory) >= self.capacity:
            print(f"❌ Inventaire plein !")
            return False
        
        self._inventory.append(new_item)
        print(f"✨ Nouveau {name} ajouté à l'inventaire")
        return True
    
    def remove_item(self, item, quantity=1):
        if item not in self._inventory:
            print(f"❌ {item.name} n'est pas dans l'inventaire")
            return False
        
        item.quantity -= quantity

        if item.quantity <= 0:
            self._inventory.remove(item)
            print(f"🗑️ {item.name} retiré de l'inventaire")
        else:
            print(f"➖ {item.name} x{quantity} retiré (Reste: {item.quantity})")

        return True
    
    def remove_item_by_name(self, name, quantity=1):
        for item in self._inventory:
            if item.name == name:
                return self.remove_item(item, quantity)
        print(f"❌ {name} introuvable dans l'inventaire")
        return False
    
    def get_item_by_index(self, index):
        if 0 <= index < len(self._inventory):
            return self._inventory[index]
        return None

    def get_item_by_name(self, name):
        for item in self._inventory:
            if item.name == name:
                return item
        return None
    
    def has_item(self, name, quantity=1):
        item = self.get_item_by_name(name)
        if item and item.quantity >= quantity:
            return True
        return False
    
    def clear(self):
        self._inventory.clear()
        print("🗑️ Inventaire vidé")
    
    def get_items_by_category(self, category):
        return [item for item in self._inventory if item.category == category]
    
    def __len__(self):
        return len(self._inventory)
    
    def __repr__(self):
        return f"Inventory({len(self._inventory)}/{self.capacity} items)"
    
    def __str__(self):
        if not self._inventory:
            return "Inventaire vide"
        return "\n".join([str(item) for item in self._inventory])