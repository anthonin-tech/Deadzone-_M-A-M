from sprites.library_item import *

RECIPES = [
    {
        "id": "Kit",
        "ingredients": {
            "Bandage": 3
        },
        "result": CARE_KIT
    },
    {
        "id": "Bandage",
        "ingredients": {
            "Tissu": 4
        },
        "result": BANDAGE
    },
    {
        "id": "Hache",
        "ingredients": {
            "Fer": 2,
            "Bois": 1,
        },
        "result": AXE
    },
    {
        "id": "Fibre",
        "ingredients": {
            "Mauvaise Herbe": 5,
        },
        "result": FIBER
    },
    {
        "id": "Tissu",
        "ingredients": {
            "Fibre": 3,
        },
        "result": FABRIC
    },
    {
        "id": "Bois Renforcé",
        "ingredients": {
            "Bois": 12,
        },
        "result": REINFORCED_WOOD
    },
    {
        "id": "Ressort",
        "ingredients": {
            "Fer": 2,
        },
        "result": SPRING
    },
    {
        "id": "Pompe",
        "ingredients": {
            "Fer": 2,
            "Bois Renforcé": 1,
            "Ressort": 3,
            "Bande Adhésive": 4,
        },
        "result": SHOTGUN
    },
]

