# 🧟 Deadzone — Survie Zombie

> Projet de Programmation Orientée Objet 
> Jeu de survie 2D top-down développé en Python avec Pygame

---

## 📋 Table des matières

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Architecture du projet](#architecture-du-projet)
- [Concepts POO mis en œuvre](#concepts-poo-mis-en-œuvre)
- [Prérequis](#prérequis)
- [Installation et lancement](#installation-et-lancement)
- [Contrôles](#contrôles)
- [Système de jeu détaillé](#système-de-jeu-détaillé)
- [Les personnages](#les-personnages)
- [Les ennemis](#les-ennemis)
- [Inventaire, équipement et craft](#inventaire-équipement-et-craft)
- [Sauvegarde](#sauvegarde)
- [Équipe](#équipe)

---

## Présentation

**Deadzone** est un jeu de survie en vue de dessus (_top-down_) dans lequel le joueur doit survivre dans une zone infestée de zombies. Il doit gérer sa faim, sa soif et sa santé tout en combattant des ennemis de différents types, en collectant des ressources, en craftant des objets et en explorant une carte multi-zone chargée depuis un fichier Tiled.

Le projet a été réalisé dans le cadre d'un cours de **Programmation Orientée Objet (POO)** de niveau B1, en mettant l'accent sur la conception de classes, l'héritage, l'encapsulation, le polymorphisme et la séparation des responsabilités.

---

## Fonctionnalités

### Gameplay principal
- Déplacement libre en vue de dessus avec détection de collisions sur les murs de la carte
- Gestion en temps réel de la **santé**, de la **faim** et de la **soif**
- **Bouclier** rechargeable automatiquement après 4 secondes sans prendre de dégâts
- Système de **projectiles** avec propriétaire, dégâts, vitesse et portée distincts
- **Aperçu de visée** affiché en temps réel : ligne pour les armes à distance, cône pour la mêlée
- Écran **Game Over** affichant les ennemis tués et le temps de survie

### Combat
- Armes **à distance** : Pistolet (1 projectile, longue portée) et Fusil à pompe (8 chevrotines, courte portée)
- Arme **de mêlée** : Hache avec arc d'attaque de 150° et portée de 15 px
- Chaque arme a une **durabilité** (100 points) qui diminue à chaque tir — l'arme est automatiquement déséquipée à 0

### Carte et exploration
- Carte chargée depuis un fichier `.tmx` (Tiled Map Editor) avec plusieurs zones interconnectées
- Zones de spawn dédiées aux ennemis, au boss et aux objets au sol
- Coffres répartis sur la carte avec un contenu prédéfini selon leur emplacement
- **Objets au sol** générés aléatoirement dans des zones de spawn spécifiques au démarrage

---

## Architecture du projet

```
Deadzone/
├── main.py                     # Point d'entrée : init Pygame et lance Game
├── game.py                     # Boucle principale (60 FPS), gestionnaire de scènes
├── map.py                      # Chargement Tiled, caméra, rendu, gestion des zones
│
├── scenes/                     # Scènes indépendantes du jeu
│   ├── menu.py                 # Menu principal + sélection de personnage + aide
│   ├── gameplay_scene.py       # Scène de jeu (spawn, update, draw, sauvegarde)
│   ├── inventory_scene.py      # Inventaire style RPG avec panneau en cuir dessiné
│   ├── craft_scene.py          # Interface de craft affichée par-dessus l'inventaire
│   ├── chest_scene.py          # Scène d'ouverture de coffre
│   └── gameover_scene.py       # Écran de fin avec statistiques
│
├── sprites/                    # Entités et objets du jeu
│   ├── player.py               # Classe Player : déplacement, tir, stats, animations
│   ├── characters.py           # MAMPlayer (base), Mahe, Maelys, Anthonin (héritage)
│   ├── enemy.py                # Enemy, FastEnemy, TankEnemy, BossEnemy + ZombieAnim
│   ├── weapon.py               # Classe Weapon avec profils pistolet / pompe / hache
│   ├── projectile.py           # Classe Projectile (position, direction, durée de vie)
│   ├── item.py                 # Classe Items avec propriétés encapsulées
│   ├── library_item.py         # Catalogue de tous les objets instanciés du jeu
│   ├── recipes.py              # Liste des recettes de craft
│   ├── chest.py                # Classe Chest (position, items, état ouvert/fermé)
│   ├── dropped_item.py         # Objet posé au sol, lié à une carte
│   └── animation.py            # Gestion des animations
│
├── systems/                    # Systèmes de jeu réutilisables
│   ├── inventory.py            # Classe Inventory : ajout, retrait, recherche, stack
│   └── crafting_manager.py     # Classe CraftingManager : vérification et exécution du craft
│
├── utils/                      # Utilitaires
│   ├── collisions.py           # Helpers de collision
│   └── helper.py               # Fonctions utilitaires générales
│
├── asset/                      # Cartes Tiled (.tmx, .tsx) et sprites de base
├── assets/
│   ├── items/                  # Icônes PNG de tous les objets
│   └── images/                 # Sprites des projectiles (pistolet, pompe, sniper, laser)
│
└── savegame.json               # Fichier de sauvegarde (généré automatiquement)
```

---

## Concepts POO mis en œuvre

### Héritage à deux niveaux

Le projet utilise un héritage à **deux niveaux** pour les personnages jouables :

```
Player                          ← sprite Pygame, stats de base, tir, équipement
  └── MAMPlayer                 ← ajoute : sprite sheet, gestion du pouvoir (actif/cooldown)
        ├── Mahe                ← activate_power() : boost de vitesse ×1.5 pendant 60s
        ├── Maelys              ← take_damage() surchargé : dégâts ÷2 pendant 60s
        └── Anthonin            ← propriété is_invisible : zombies ignorent le joueur
```

La hiérarchie des ennemis illustre également l'héritage avec spécialisation :

```
Enemy                           ← IA de base : détection, poursuite, attaque, HP bar
  ├── FastEnemy                 ← vitesse 70, 20 PV, animation 3 frames
  ├── TankEnemy                 ← vitesse 28, 150 PV, rayon de collision 9
  └── BossEnemy                 ← machine à états (IDLE/CHASE/CASTING/RECOVERY),
                                   3 compétences, 3 phases de puissance
```

### Encapsulation

La classe `Items` protège tous ses attributs via des **propriétés Python** (`@property` / `@setter`) :

```python
class Items:
    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        self._quantity = max(0, value)        # quantité toujours >= 0

    @property
    def durability(self):
        return self._durability

    @durability.setter
    def durability(self, value):
        self._durability = max(0, min(100, value))  # durabilité clampée entre 0 et 100
```

De même, `Inventory` encapsule sa liste interne `_inventory` et ne l'expose qu'en lecture via la propriété `items`.

### Polymorphisme

Chaque sous-classe d'`Enemy` redéfinit `_get_raw()` pour retourner son propre sprite généré de façon procédurale par `ZombieAnim`. `BossEnemy` surcharge également `update()` en intégrant une **machine à états** complète, et `draw()` pour afficher le cercle de l'AoE.

`Maelys` surcharge `take_damage()` pour diviser les dégâts par 2 pendant l'activation de son pouvoir, sans modifier la logique de la classe parente.

### Séparation des responsabilités (SRP)

| Classe | Responsabilité unique |
|--------|-----------------------|
| `Inventory` | Stocker et rechercher des objets (ajout, retrait, stack, recherche par nom/catégorie) |
| `CraftingManager` | Vérifier les ingrédients disponibles et exécuter la transformation |
| `Weapon` | Centraliser les profils d'armes et créer les projectiles selon le type d'attaque |
| `Game` | Maintenir la boucle de jeu et déléguer à la scène courante |
| `Gameplay_Scene` | Orchestrer le monde (spawn, collisions, projectiles, sauvegarde) |

### Gestion des scènes (pattern State)

La classe `Game` maintient une référence `current_scene` et délègue systématiquement `handle_event()`, `update()` et `draw()` à la scène active. Changer de scène revient à remplacer cette référence via `game.change_scene()`.

---

## Prérequis

- **Python** >= 3.10
- **Pygame** >= 2.0
- **pytmx** (chargement des cartes Tiled)

---

## Installation et lancement

```bash
# 1. Cloner le dépôt
git clone https://github.com/anthonin-tech/Deadzone-_M-A-M.git
cd "Deadzone-_M-A-M/Deadzone"

# 2. Installer les dépendances
pip install pygame pytmx

# 3. Lancer le jeu
python main.py
```

---

## Contrôles

### En jeu

| Touche | Action |
|--------|--------|
| `Z` `Q` `S` `D` | Déplacement (haut / gauche / bas / droite) |
| `Clic gauche` | Tirer / Attaquer |
| `E` | Ramasser un objet au sol ou ouvrir un coffre |
| `TAB` | Ouvrir / Fermer l'inventaire |
| `P` | Activer le pouvoir spécial du personnage |
| `M` | Mettre en pause et afficher les instructions |
| `F5` | Sauvegarder la partie |
| `Échap` | Retourner au menu principal |

### Dans l'inventaire

| Touche / Action | Effet |
|-----------------|-------|
| `Clic gauche` sur un objet consommable | Utiliser l'objet (soin, nourriture, boisson) |
| `Clic gauche` sur un slot d'équipement | Déséquiper l'objet |
| `Clic droit` sur un objet | Jeter 1 exemplaire de l'objet |
| `E` avec un objet survolé | Équiper l'objet (arme ou armure) |
| `C` | Ouvrir / Fermer le menu de craft |
| `TAB` ou `Échap` | Fermer l'inventaire et retourner en jeu |

---

## Système de jeu détaillé

### Survie

Le joueur possède trois jauges qui diminuent en continu :

- **Santé** (100 PV max) : diminue si la faim ou la soif atteint 0 (perte de 1 PV/s)
- **Soif** (50 max) : diminue de 0,03/s en permanence
- **Faim** (50 max) : diminue de 0,03/s en permanence

Un **bouclier** s'ajoute par-dessus la santé lorsque de l'armure est équipée. Il se régénère automatiquement au rythme de 12 points/s après 4 secondes sans subir de dégâts. Les dégâts reçus absorbent d'abord le bouclier avant d'attaquer la santé.

### Armes et durabilité

```python
# Extrait de weapon.py — profils des armes
PROFILES = {
    "pistol":  { "cooldown_ms": 320,  "projectile_speed": 700, "damage": 12,
                 "pellets": 1, "spread_deg": 1.5, "max_distance": 75 },
    "shotgun": { "cooldown_ms": 900,  "projectile_speed": 540, "damage": 4,
                 "pellets": 8, "spread_deg": 18,  "max_distance": 50 },
    "axe":     { "cooldown_ms": 1000, "attack_type": "melee",
                 "melee_damage": 10,  "melee_range": 15, "melee_arc_deg": 150 }
}
```

Chaque tir décrémente la durabilité de l'arme de 5 points. À 0, l'arme est automatiquement retirée de l'emplacement d'équipement. La hache vérifie les ennemis dans un arc de 150° devant le joueur et inflige les dégâts directement sans créer de projectile.

### Spawn des ennemis

Les ennemis sont initialement placés dans les zones de spawn définies sur la carte Tiled. Un **timer de 15 secondes** déclenche ensuite un respawn de 1 à 2 ennemis supplémentaires par zone. La répartition pondérée favorise les zombies normaux :

```python
random.choice([Enemy, Enemy, Enemy, FastEnemy, TankEnemy])
```

### Coffres

Les coffres sont chargés automatiquement depuis les objets Tiled (dont le nom contient `"chest"`). Leur contenu est prédéfini selon leur identifiant de carte. Exemples :

| Coffre | Contenu |
|--------|---------|
| `bunker` | Pistolet, Bande Adhésive, Eau, Bois x2, Bandage |
| `cave_3` | Fer x3, Casque Masque à gaz, Bande Adhésive, Kit de Soin |
| `class` | Bande Adhésive, Plastron Haut de Soldat, Kit de Soin |
| `canteen` | Viande x3, Eau x2 |

---

## Les personnages

Les trois personnages jouables héritent tous de `MAMPlayer` qui hérite lui-même de `Player`. Chacun possède un **pouvoir spécial** activé avec `P`, avec une durée active de **60 secondes** et un cooldown de **60 secondes** après expiration.

### Mahé — Boost de vitesse
Multiplie la vitesse de déplacement par **1,5** pendant toute la durée active. La vitesse originale est sauvegardée et restaurée automatiquement à l'expiration du pouvoir.

```python
class Mahe(MAMPlayer):
    SPEED_MULTIPLIER = 1.5

    def activate_power(self):
        self.original_speed = self.speed
        self.speed *= self.SPEED_MULTIPLIER
        ...
    
    def update_power(self):
        # Restaure la vitesse quand le pouvoir expire
        if self.power_active and now - self._power_start >= self.POWER_DURATION:
            self.speed = self.original_speed
```

### Maëlys — Bouclier
Surcharge `take_damage()` pour diviser les dégâts reçus **par 2** (minimum 1) tant que le pouvoir est actif. Aucun changement de comportement en dehors de l'activation.

```python
class Maelys(MAMPlayer):
    def take_damage(self, amount, attacker_x=None, attacker_y=None):
        if self.power_active:
            amount = max(1, amount // 2)
        super().take_damage(amount, attacker_x, attacker_y)
```

### Anthonin — Invisibilité
Expose une propriété `is_invisible`. Lorsqu'elle vaut `True`, la `Gameplay_Scene` passe `None` en guise de joueur à chaque `enemy.update()`, ce qui empêche tous les ennemis de le détecter ou de l'attaquer.

```python
class Anthonin(MAMPlayer):
    @property
    def is_invisible(self):
        return self.power_active

# Dans Gameplay_Scene.update_enemies() :
if player_invisible:
    enemy.update(dt, None, self.enemies, self.projectiles)
```

---

## Les ennemis

### Zombie normal (`Enemy`)
- **PV** : 30 | **Vitesse** : 45 | **Dégâts** : 6 | **Cooldown attaque** : 1 400 ms
- **Détection** : 150 px | **Portée d'attaque** : 14 px
- Animation 2 frames, sprites générés procéduralement pixel par pixel par `ZombieAnim.normal()`

### Zombie rapide (`FastEnemy`)
- **PV** : 20 | **Vitesse** : 70 | **Dégâts** : 5 | **Cooldown attaque** : 1 200 ms
- Animation 3 frames (course plus fluide), yeux jaunes distinctifs

### Zombie tank (`TankEnemy`)
- **PV** : 150 | **Vitesse** : 28 | **Dégâts** : 12 | **Cooldown attaque** : 2 000 ms
- Rayon de collision agrandi (9 px) pour simuler la corpulence

### Boss (`BossEnemy`) — Machine à états

Le boss fonctionne avec 4 états (`IDLE`, `CHASE`, `CASTING`, `RECOVERY`) et **3 phases** déclenchées par seuils de PV :

| Phase | Déclencheur | Effet |
|-------|------------|-------|
| Phase 1 | > 70 % PV | Comportement standard |
| Phase 2 | <= 70 % PV | AoE plus forte, invocations disponibles |
| Phase 3 | <= 40 % PV | Double projectile, yeux rouges, invocations renforcées |

**Compétences** (sélectionnées en tournant, cooldown global de 6 s) :

| Compétence | Cooldown | Description |
|------------|---------|-------------|
| `projectile` | 5 s | Tire 1 à 2 projectiles rapides (vitesse 220) vers le joueur |
| `aoe` | 10 s | Inflige 12 (ou 20 en phase 3) dégâts si le joueur est à <= 120 px |
| `summon` | 18 s | Invoque 2 à 3 zombies normaux + 1 à 2 rapides autour de lui |

---

## Inventaire, équipement et craft

### Inventaire (`Inventory`)

Capacité de **35 emplacements**. Les objets des catégories `ressource`, `soin`, `nourriture` et `boisson` s'empilent automatiquement si le même objet existe déjà. Les armes et armures occupent chacune un emplacement distinct.

```python
def add_item(self, item, quantity=None):
    if self._is_stackable(item):          # ressources, soins, nourriture, boissons
        for existing in self._inventory:
            if existing.is_same_item(item):
                existing.quantity += qty  # empilement automatique
                return True
    if len(self._inventory) >= self.capacity:
        return False                      # inventaire plein
    self._inventory.append(item)
    return True
```

### Équipement

4 emplacements dédiés : **arme**, **casque**, **plastron**, **bottes**. Équiper un objet le retire de l'inventaire. Déséquiper le remet dans l'inventaire. Chaque pièce d'armure ajoute des points de bouclier maximum et le recalcul est automatique.

### Catalogue des objets

| Objet | Catégorie | Rareté | Effet |
|-------|-----------|--------|-------|
| Kit de Soin | soin | Légendaire | +30 PV |
| Bandage | soin | Rare | +7 PV |
| Viande | nourriture | Rare | +12 faim |
| Eau | boisson | Rare | +12 soif |
| Pistolet | arme | Rare | — |
| Pompe | arme | Légendaire | — |
| Hache | arme | Commun | — |
| Casque Casquette | armure | Rare | +7 bouclier |
| Plastron T-shirt | armure | Rare | +13 bouclier |
| Botte Jeans | armure | Rare | +10 bouclier |
| Casque Masque à gaz | armure | Épique | +15 bouclier |
| Plastron Haut de Soldat | armure | Épique | +30 bouclier |
| Botte Bas de Soldat | armure | Épique | +15 bouclier |

### Recettes de craft

Le `CraftingManager` délègue entièrement la vérification des ressources à l'`Inventory`. S'il peut crafter, il consomme les ingrédients et ajoute une copie de l'objet résultat via `copy.copy()`.

| Recette | Ingrédients |
|---------|-------------|
| Fibre | 5x Mauvaise Herbe |
| Tissu | 3x Fibre |
| Bandage | 4x Tissu |
| Kit de Soin | 3x Bandage |
| Ressort | 2x Fer |
| Bois Renforcé | 12x Bois |
| Hache | 2x Fer + 1x Bois |
| Fusil à Pompe | 2x Fer + 4x Bois Renforcé + 3x Ressort + 4x Bande Adhésive |

---

## Sauvegarde

La sauvegarde (touche `F5`) sérialise en **JSON** l'état complet de la partie :

- Classe et position du joueur, santé actuelle
- Contenu de l'inventaire (id + quantité)
- Objets posés au sol (id, position, carte associée)
- État de chaque ennemi (type, position, PV restants)
- Contenu des coffres déjà ouverts
- Nombre d'ennemis tués, temps de jeu écoulé
- Flag `boss_defeated` pour ne pas faire réapparaître le boss vaincu

Le chargement reconstruit chaque entité dynamiquement grâce à `ITEMS_BY_NAME` et `globals().get(class_name)`.

---

## Équipe

•**Anthonin** 
•**Mahé** 
•**Maëlys** 

---

> *Projet réalisé dans le cadre du cursus Bachelor — Programmation Orientée Objet, niveau B1.*
