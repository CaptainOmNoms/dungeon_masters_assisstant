from operator import attrgetter
from cmd2 import Cmd
from monster_tracker.dice import Dice
#from monster_tracker.models import Encounter, Monster, Hero
from monster_tracker.encounter import EncounterOld
from monster_tracker.character import Status
from monster_tracker.monster import MonsterOld

# TODO: lookup to table function or custom

#ENC = Encounter()


def add_npc(enc):
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative_bonus = input("Initiative Bonus: ")
    speed = input("Speed: ")
    enc.add_npc(name, health, ac, initiative_bonus, speed)


def add_pc(enc):
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative_bonus = input("Initiative Bonus: ")
    speed = input("Speed: ")
    player = input("Played By: ")
    enc.add_player(name, health, ac, initiative_bonus, speed, player)


class App(Cmd):
    def __init__(self):
        super().__init__()
        self.enc = EncounterOld()
        self.current_player = None

    def do_hello(self, arg):
        print('Hello world')

    def do_add_npc(self, arg):
        add_npc(self.enc)

    def do_print_encounter(self, arg):
        print(self.enc)
        #for key, item in self.enc.creatures.items():
        #   item.print()

    def do_add_pc(self, arg):
        add_pc(self.enc)

    def do_set_initiatives(self):
        die = Dice(1, 20)
        for key, item in self.enc.creatures.items():
            roll = 0
            while not roll:
                roll = die.check_roll(
                    input("Enter initiative roll for {0}: ".format(key)))
            item.initiative = roll + item.initiative_bonus

        # TODO figure out what's going on here. Dicts are inherently unsorted so this does literally nothing
        # since self.enc.creatures is a dict
        sorted(self.enc.creatures,
            key=attrgetter('initiative_bonus', 'initiative'),
            reverse=True)

    def do_heal(self, creature, health_up):
        if health_up > 0:
            self.enc.creatures[creature].heal(health_up)

    def do_damage(self, done_by, done_to, damage, type):
        self.deal_damage(done_by, done_to, damage, type)

    def do_next(self, num):
        self.current_player = self.enc.creatures[num]
        if self.current_player.status == Status.ALIVE:
            self.current_player.do_turn()
        if self.current_player.status == Status.UNCONSCIOUS:
            self.current_player.dead()

    def do_encounter(self):
        turn = 0
        while True:
            self.do_print_encounter('')
            self.do_set_initiatives()
            self.do_next(turn)
            turn += 1
            if len(self.creatures) == turn:
                turn = 0

    def do_load_from_cfg(self, arg):
        pass


if __name__ == '__main__':
    App().cmdloop()
