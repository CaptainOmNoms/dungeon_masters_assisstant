from cmd2 import Cmd
from .encounter import *

# TODO: loopup to table function or custom

ENC = Encounter()


def add_npc():
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative = input("Initiative: ")
    speed = input("Speed: ")
    ENC.add_npc(name, health, ac, initiative, speed)


def add_pc():
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative = input("Initiative: ")
    speed = input("Speed: ")
    player = input("Played By: ")
    ENC.add_player(name, health, ac, initiative, speed, player)


class App(Cmd):
    def do_hello(self, arg):
        print('Hello world')

    def do_add_npc(self, arg):
        add_npc()

    def do_print_encounter(self, arg):
        for key, item in monsters.items():
            print("{}, {}, {}, {}, {}".format)

    def do_add_pc(self, arg):
        add_pc()


if __name__ == '__main__':
    App().cmdloop()
