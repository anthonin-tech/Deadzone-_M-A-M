import os
import time
from sprites.player import Mahe, Maelys, Anthonin  # ton fichier avec les classes

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\nAppuie sur Entrée pour continuer...")

def show_title():
    print("===================================")
    print("        🧟 DEADZONE GAME 🧟")
    print("===================================")


def character_menu():
    clear()
    show_title()
    print("\nChoisis ton personnage :")
    print("1 - Mahé 🥊 (gros dégâts)")
    print("2 - Maëlys 🎾 (bouclier)")
    print("3 - Anthonin 🧟 (invisible zombies)")
    print("0 - Retour")

    choice = input("Votre choix: ")
    if choice == "1":
        return Mahe()
    elif choice == "2":
        return Maelys()
    elif choice == "3":
        return Anthonin()
    else:
        return None


def help_menu():
    clear()
    show_title()
    print("\n🎮 Commandes :")
    print("p → activer la capacité")
    print("s → afficher le statut")
    print("q → quitter la partie")
    print("\n⏱️ Capacités :")
    print("- Durée : 1 min pour tester ici (réglable)")
    print("- Recharge : 1 min")
    pause()


def controls(player):
    while True:
        player.update_power()
        print("\nSTATUT DU JOUEUR")
        print(player)

        print("\nCommandes :")
        print("p → activer capacité")
        print("s → afficher statut")
        print("q → quitter")

        cmd = input("> ").lower()
        if cmd == "p":
            player.activate_power()
        elif cmd == "s":
            print(player)
        elif cmd == "q":
            break
        time.sleep(0.5)


def main_menu():
    player = None

    while True:
        clear()
        show_title()
        print("\n1 - Jouer")
        print("2 - Choisir personnage")
        print("3 - Aide")
        print("0 - Quitter")

        choice = input("Votre choix: ")
        if choice == "1":
            if player is None:
                print("\n⚠️ Choisis d'abord un personnage !")
                time.sleep(1.5)
            else:
                print(f"Vous avez choisi {player}")
                controls(player)
        elif choice == "2":
            player = character_menu()
        elif choice == "3":
            help_menu()
        elif choice == "0":
            print("\n👋 À bientôt !")
            break

if __name__ == "__main__":
    main_menu()
