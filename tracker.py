from cmd2 import Cmd
from .dice import Dice
from operator import attrgetter
from .models import Encounter

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
        add_npc()

    def do_print_encounter(self, arg):
        for key, item in ENC.creatures.items():
            item.print()

    def do_add_pc(self, arg):
        add_pc()

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

    def do_next(self):
        pass
        # changes self.current_player to next in order
        if self.current_creature.status != 'dead':
            # this allows us to keep them on screen and in the initiative
            # which will help for when we have a GUI
            # prints stats for current player
            # self.current_player.begin_turn()

    def do_encounter(self):
        pass


if __name__ == '__main__':
    App().cmdloop()
