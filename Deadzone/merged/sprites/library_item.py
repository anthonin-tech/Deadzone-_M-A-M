from sprites.item import Items

CARE_KIT = Items(
    name = "Kit de Soin",
    category = "soin",
    rarity = "Legendary",
    illustration = "Kit_Soin.png",
    description = "Permet de se soigne 30 PV",
    effect = 30
)

BANDAGE = Items(
    name = "Bandage",
    category = "soin",
    rarity = "Rare",
    illustration = "Bandage_Soin.png",
    description = "Permet de se soigne 7 PV",
    effect = 7
)

MEAT = Items(
    name = "Viande",
    category = "nourriture",
    rarity = "rare",
    illustration = "Viande_Nourriture.png",
    description = "Rassasit de 12",
    effect = 12
)

WATER = Items(
    name = "Eau",
    category = "nourriture",
    rarity = "rare",
    illustration = "Eau_Nourriture.png",
    description = "Hydrate de 12 et cette fois il boit tout",
    effect = 12
)

SHOTGUN = Items(
    name = "Pompe",
    category = "arme",
    rarity = "legendary",
    illustration = "Pompe_Arme.png",
    description = "Arme très puissante à semi-distance"
)

GUN = Items(
    name = "Pistolet",
    category = "arme",
    rarity = "rare",
    illustration = "Pistolet_Arme.png",
    description = "Arme utile à long distance"
)

AXE = Items(
    name = "Hache",
    category = "arme",
    rarity = "commun",
    illustration = "Hache_Arme.png",
    description = "Arme très forte au corps à corps",
)

CAP = Items(
    name = "Casque - Casquette",
    category = "armure",
    rarity = "rare",
    illustration = "Casque_Armure.png",
    description = "Apporte 7 points d'armure avec du style",
    effect = 7
)

TSHIRT = Items(
    name = "Plastron - T-shirt",
    category = "armure",
    rarity = "rare",
    illustration = "Tshirt_Armure.png",
    description = "Apporte 13 points d'armure et réchauffe",
    effect = 13
)

PANTS = Items(
    name = "Botte - Jeans",
    category = "armure",
    rarity = "rare",
    illustration = "Jean_Armure.png",
    description = "Apporte 10 points d'armure",
    effect = 10
)

HELMET_SOLDAT =Items(
    name = "Casque - Masque à gaz",
    category = "armure",
    rarity = "épique",
    illustration = "Casque_Soldat_Armure.png",
    description = "Apporte 15 points d'armure",
    effect = 15
)

CHESPLATE_SOLDAT =Items(
    name = "Plastron - Haut de Soldat",
    category = "armure",
    rarity = "épique",
    illustration = "Tshirt_Soldat_Armure.png",
    description = "Apporte 30 points d'armure",
    effect = 30
)

BOTTS_SOLDAT =Items(
    name = "Botte - Bas de Soldat",
    category = "armure",
    rarity = "épique",
    illustration = "Jean_Soldat_Armure.png",
    description = "Apporte 15 points d'armure",
    effect = 15
)

WOOD =Items(
    name = "Bois",
    category = "ressource",
    rarity = "commun",
    illustration = "Bois_Ressource.png",
    description = "On peut construire des choses avec le bois",
)

IRON =Items(
    name = "Fer",
    category = "ressource",
    rarity = "rare",
    illustration = "Fer_Ressource.png",
    description = "On peut forger des choses avec le fer",
)

ITEMS_BY_NAME = {
    "CARE_KIT": CARE_KIT,
    "BANDAGE": BANDAGE,
    "MEAT": MEAT,
    "WATER": WATER,
    "SHOTGUN": SHOTGUN,
    "GUN": GUN,
    "AXE": AXE,
    "CAP": CAP,
    "TSHIRT": TSHIRT,
    "PANTS": PANTS,
    "HELMET_SOLDAT": HELMET_SOLDAT,
    "CHESPLATE_SOLDAT": CHESPLATE_SOLDAT,
    "BOTTS_SOLDAT": BOTTS_SOLDAT,
    "WOOD": WOOD,
    "IRON": IRON
}