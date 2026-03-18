import sys
import copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from sprites.recipes import RECIPES
from sprites.item import Items

class CraftingManager:
    def __init__(self, inventory):
        self.inventory = inventory

    def get_available_recipes(self):
        return [r for r in RECIPES if self.can_craft(r)]

    def can_craft(self, recipe):
        for item_name, qty_needed in recipe["ingredients"].items():
            if not self.inventory.has_item(item_name, qty_needed):
                return False
        return True

    def craft(self, recipe):
        if not self.can_craft(recipe):
            return False

        for item_name, quantity in recipe["ingredients"].items():
            self.inventory.remove_item_by_name(item_name, quantity)

        crafted_item = copy.copy(recipe["result"]) 
        crafted_item.quantity = 1
        self.inventory.add_item(crafted_item)

        return True
