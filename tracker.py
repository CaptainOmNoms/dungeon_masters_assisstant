from cmd2 import Cmd
from .encounter import *
from .dice import *
from operator import attrgetter

# TODO: lookup to table function or custom

ENC = Encounter()


def add_npc():
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative_bonus = input("Initiative Bonus: ")
    speed = input("Speed: ")
    ENC.add_npc(name, health, ac, initiative_bonus, speed)


def add_pc():
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative_bonus = input("Initiative Bonus: ")
    speed = input("Speed: ")
    player = input("Played By: ")
    ENC.add_player(name, health, ac, initiative_bonus, speed, player)


class App(Cmd):
    def do_hello(self, arg):
        print('Hello world')

    def do_add_npc(self, arg):
        name = input("Name: ")
        health = input("Health: ")
        ac = input("Armor Class: ")
        initiative_bonus = input("Initiative Bonus: ")
        speed = input("Speed: ")
        ENC.add_npc(name, health, ac, initiative_bonus, speed)


    def do_print_encounter(self, arg):
        for key, item in ENC.creatures.items():
            item.print()

    def do_add_pc(self, arg):
        name = input("Name: ")
        health = input("Health: ")
        ac = input("Armor Class: ")
        initiative_bonus = input("Initiative Bonus: ")
        speed = input("Speed: ")
        player = input("Played By: ")
        ENC.add_player(name, health, ac, initiative_bonus, speed, player)

    def do_set_initiatives(self):
        die = Dice(1, 20)
        for key, item in ENC.creatures.items():
            roll = 0
            while not roll:
                roll = die.check_roll(input("Enter initiative roll for {0}: ".format(key)))
            item.initiative = roll + item.initiative_bonus
        ENC.creatures = sorted(ENC.creatures, key=attrgetter('initiative_bonus', 'initiative'), reverse=True)

    def do_heal(self, creature, health_up): # too many different ways to heal to do dice validation here
        if health_up > 0:
            ENC.creatures[creature].heal(health_up)

    def do_damage(self, creature, health_down): # too many different ways to damage to do dice validation here
        # TODO: make generic actors
        if health_down > 0:
            ENC.creatures[creature].heal(health_down)

    def do_next(self, id):
        self.current_player = self.creatures[id]
        if self.current_player.status == 'dead':
            if self.current_player.isinstance(Monster):
                self.total_xp += self.current_player.xp
        if self.current_player.status == 'alive':
            self.current_player.do_turn()
        if self.current_player.status == 'unconscious':
            self.current_player.dead()

    def do_encounter(self):
        ENC = Encounter()
        turn = 0
        while True:
            ENC.do_print_encounter()
            ENC.do_set_initiatives()
            ENC.do_next(turn)
            turn += 1





if __name__ == '__main__':
    App().cmdloop()
