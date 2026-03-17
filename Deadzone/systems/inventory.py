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

    def _is_stackable(self, item):
        category = getattr(item, "category", None)
        return category not in ("arme", "armure")

    def add_item(self, item, quantity=1):
        if self._is_stackable(item):
            for existing in self._inventory:
                if existing.is_same_item(item):
                    existing.quantity += quantity
                    return True

        if len(self._inventory) >= self.capacity:
            return False

        self._inventory.append(item)
        return True

    def remove_item(self, item, quantity=1):
        if item not in self._inventory:
            return False

        item.quantity -= quantity

        if item.quantity <= 0:
            self._inventory.remove(item)

        return True

    def remove_item_by_name(self, name, quantity=1):
        for item in self._inventory:
            if item.name == name:
                return self.remove_item(item, quantity)
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

    def get_items_by_category(self, category):
        return [item for item in self._inventory if item.category == category]

    def __len__(self):
        return len(self._inventory)

    def __repr__(self):
        return f"Inventory({len(self._inventory)}/{self.capacity} items)"

    def __str__(self):
        return "\n".join([str(item) for item in self._inventory])
