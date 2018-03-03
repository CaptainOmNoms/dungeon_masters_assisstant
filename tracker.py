from .encounter import *


def main_menu():
    print("""
    1. Add Monster
    2. Add NPC Hero
    3. Add PC
    4. Run Encounter
    5. Exit""")


#def add_monster():
#TODO: loopup to table function or custom


def add_npc():
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative = input("Initiative: ")
    speed = input("Speed: ")
    Encounter.add_npc(name, health, ac, initiative, speed)


def add_pc():
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative = input("Initiative: ")
    speed = input("Speed: ")
    player = input("Played By: ")
    Encounter.add_player(name, health, ac, initiative, speed, player)


def encounter():
    for key, item in monsters.items():
        print("{0}, {1}, {2}, {3}, {4}".format)


loop = True

while loop:
    main_menu()
    choice = input("Choose an Option: ")

    if choice == '1':
        #add_monster()
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
