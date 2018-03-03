from Encounter import *

battle = Encounter()

def main_menu():
    print("""
    1. Add Monster
    2. Add NPC Hero
    3. Add PC 
    4. Run Encounter
    5. Exit""")


# def add_monster():
# TODO: loopup to table function or custom

def add_npc():
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative_bonus = input("Initiative Bonus: ")
    speed = input("Speed: ")
    battle.add_npc(name, health, ac, initiative_bonus, speed)


def add_pc():
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative_bonus = input("Initiative Bonus: ")
    speed = input("Speed: ")
    player = input("Played By: ")
    battle.add_player(name, health, ac, initiative_bonus, speed, player)


def encounter():
    for key, item in battle.creatures.items():
        item.print()

loop = True

while loop:
    main_menu()
    choice = input("Choose an Option: ")

    if choice == '1':
        # add_monster()
        loop = True
    elif choice == '2':
        add_npc()
    elif choice == '3':
        add_pc()
    elif choice == '4':
        encounter()
    elif choice == '5':
        loop = False
    else:
        input('Invalid option. Press ENTER to return to the menu')
