from sprites.item import Items

CARE_KIT = Items(
    name = "Kit de Soin",
    category = "soin",
    rarity = "legendaire",
    illustration = "Kit_Soin.png",
    description = "Permet de se soigne 30 PV",
    effect = 30
)

BANDAGE = Items(
    name = "Bandage",
    category = "soin",
    rarity = "rare",
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
    rarity = "legendaire",
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
    rarity = "epique",
    illustration = "Casque_Soldat_Armure.png",
    description = "Apporte 15 points d'armure",
    effect = 15
)

CHESPLATE_SOLDAT =Items(
    name = "Plastron - Haut de Soldat",
    category = "armure",
    rarity = "epique",
    illustration = "Tshirt_Soldat_Armure.png",
    description = "Apporte 30 points d'armure",
    effect = 30
)

BOTTS_SOLDAT =Items(
    name = "Botte - Bas de Soldat",
    category = "armure",
    rarity = "epique",
    illustration = "Jean_Soldat_Armure.png",
    description = "Apporte 15 points d'armure",
    effect = 15
)

WOOD =Items(
    name = "Bois",
    category = "ressource",
    rarity = "rare",
    illustration = "Bois_Ressource.png",
    description = "On peut construire des choses avec le bois",
)

REINFORCED_WOOD =Items(
    name = "Bois Renforcée",
    category = "ressource",
    rarity = "epique",
    illustration = "Bois_Renforcée_Ressource.png",
    description = "C'est un bois très puissant",
)

IRON =Items(
    name = "Fer",
    category = "ressource",
    rarity = "epique",
    illustration = "Fer_Ressource.png",
    description = "On peut forger des choses avec le fer",
)

WEED =Items(
    name = "Mauvaise Herbe",
    category = "ressource",
    rarity = "commun",
    illustration = "Mauvaise_Herbe_Ressource.png",
    description = "La mauvaise herbe peut être utile",
)

FIBER =Items(
    name = "Fibre",
    category = "ressource",
    rarity = "rare",
    illustration = "Fibre_Ressource.png",
    description = "Il est aussi solide que du papier",
)

SPRING = Items(
    name = "Ressort",
    category = "ressource",
    rarity = "epique",
    illustration = "Ressort_Ressource.png",
    description = "C'est rebondissant et très utile pour le pompe",
)

ADHESIVE_TAPE = Items(
    name = "Bande Adhésive",
    category = "ressource",
    rarity = "rare",
    illustration = "Bande_Adhésive_Ressource.png",
    description = "C'est rebondissant et très utile pour le pompe",
)

FABRIC = Items(
    name = "Tissu",
    category = "ressource",
    rarity = "epique",
    illustration = "Tissu_Ressource.png",
    description = "Utile pour ce faire des bandages",
)
