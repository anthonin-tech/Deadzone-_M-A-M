class Items:
    def __init__(self, name, durability, category, rarity, illustration, quantity=1):
        self._name = name 
        self._durability = durability
        self._category = category
        self._rarity = rarity
        self._quantity = quantity
        self._illustration = illustration
        self.image_surface = None

    @property
    def name(self):
        return self._name

    @property
    def durability(self):
        return self._durability
    
    @durability.setter
    def durability(self, value):
        self._durability = max(0, min(100, value))

    @property
    def category(self):
        return self._category

    @property
    def rarity(self):
        return self._rarity

    @property
    def quantity(self):
        return self._quantity
    
    @quantity.setter
    def quantity(self, value):
        self._quantity = max(0, value)

    @property
    def illustration(self):
        return self._illustration

    def is_same_item(self, other):
        if not isinstance(other, Items):
            return False
        return (
            self._name == other._name and 
            self._category == other._category and 
            self._rarity == other._rarity and
            self._illustration == other._illustration
        )

    def use(self):
        if self._quantity > 0:
            self._quantity -= 1
            return True
        return False
    
    def __repr__(self):
        return f"Items(name='{self._name}', qty={self._quantity}, rarity='{self._rarity}')"
    
    def __str__(self):
        return f"{self._name} x{self._quantity} ({self._rarity})"