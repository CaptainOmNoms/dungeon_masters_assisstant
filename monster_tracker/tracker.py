from itertools import cycle
from operator import attrgetter
from cmd2 import Cmd
from more_itertools import peekable, consume
from monster_tracker.dice import Dice
from monster_tracker.models import Encounter, Monster, Hero, s, Status

# TODO: lookup to table function or custom


def add_npc(s, enc):
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative_bonus = input("Initiative Bonus: ")
    speed = input("Speed: ")
    pc = Hero(name, health, ac, initiative_bonus, speed)
    s.add(pc)
    pc.encounter_id = enc.id
    s.commit()


def add_pc(s, enc):
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative_bonus = input("Initiative Bonus: ")
    speed = input("Speed: ")
    player = input("Played By: ")
    pc = Hero(name, health, ac, initiative_bonus, speed)
    pc.encounter_id = enc.id
    s.add(pc)
    s.commit()


class App(Cmd):

    def __init__(self):
        super().__init__()
        self.enc = Encounter()
        self.current_player = None
        self.session = s
        self.enc.init_order = []

    def do_hello(self, arg):
        print('Hello world')

    def do_add_npc(self, arg):
        add_npc(self.session, self.enc)

    def do_print_encounter(self, arg):
        print(self.enc)
        #for key, item in self.enc.creatures.items():
        #   item.print()

    def do_add_pc(self, arg):
        add_pc(self.session, self.enc)

    def do_set_initiatives(self):
        die = Dice(1, 20)
        for key, item in self.enc.creatures.items():
            roll = 0
            while not roll:
                roll = die.check_roll(input("Enter initiative roll for {0}: ".format(key)))
            item.initiative = roll + item.initiative_bonus

        self.enc.init_order = sorted(self.enc.creatures, key=attrgetter('initiative_bonus', 'initiative'), reverse=True)

    # TODO rewrite
    def do_heal(self, creature, health_up):
        # too many different ways to heal to do dice validation here
        if health_up > 0:
            self.enc.creatures[creature].heal(health_up)

    # TODO rewrite
    def do_damage(self, creature, health_down):
        # too many different ways to damage to do dice validation here
        # TODO: make generic actors
        if health_down > 0:
            self.enc.creatures[creature].heal(health_down)

    #def do_next(self):
    #    self.current_player = self.enc.creatures[id]
    #    if self.current_player.status == Status.DEAD:
    #        if isinstance(self.current_player, Monster):
    #            self.enc.total_xp += self.current_player.xp
    #    if self.current_player.status == Status.ALIVE:
    #        self.current_player.do_turn()
    #    if self.current_player.status == Status.UNCONSCIOUS:
    #        self.current_player.dead()

    def do_encounter(self):
        self.do_print_encounter('')
        self.do_set_initiatives()
        next_char = None
        while True:
            init_order = peekable(cycle(self.enc.init_order))
            if next_char:
                consume(init_order, next_char)
                next_char = None
            for creature in init_order:
                # do setup things for each turn here
                self.current_player = self.enc.creatures[creature]
                if self.current_player.status == Status.ALIVE:
                    self.current_player.do_turn()
                # So what we're saying here is that any creature that drops to 0 health will automatically become
                # unconsious. Then, when they call Character.dead() they will have their status set to DEAD
                # This way we can clean up Heros and Monsters alike
                if self.current_player.status == Status.UNCONSCIOUS:
                    ret = self.current_player.dead()
                    if ret:
                        if isinstance(ret, Monster):
                            self.enc.total_xp += ret
                        self.enc.init_order.remove(creature)
                        # By breaking here, we exit the for loop
                        # This will cause a recomputation of the circular list
                        # We then get the next item in the list
                        next_char = self.enc.init_order.index(init_order.peek())
                        break

    def do_load_from_cfg(self, arg):
        pass


if __name__ == '__main__':
    App().cmdloop()
