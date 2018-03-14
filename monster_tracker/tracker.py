from itertools import cycle
from operator import attrgetter
from cmd2 import Cmd
from more_itertools import peekable, consume
import ui
from monster_tracker.dice import Dice
from monster_tracker.models import Encounter, Monster, Hero, s, Status

# TODO: lookup to table function or custom <- no longer necessary?


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
    return pc


def add_pc(s, enc):
    name = input("Name: ")
    health = input("Health: ")
    ac = input("Armor Class: ")
    initiative_bonus = input("Initiative Bonus: ")
    speed = input("Speed: ")
    player = input("Played By: ")
    pc = Hero(name, health, ac, initiative_bonus, speed, player)
    pc.encounter_id = enc.id
    s.add(pc)
    s.commit()
    return pc


class App(Cmd):

    def __init__(self):
        super().__init__()
        self.enc = None
        self.current_player = None
        self.session = s

    def do_add_npc(self, arg):
        if not self.enc:
            if not ui.ask_yes_no('There is no encounter set. Would you like to set it before proceeding?'):
                return
        pc = add_npc(self.session, self.enc)
        if self.enc:
            self.enc.characters[pc.name] = pc

    def do_add_pc(self, arg):
        if not self.enc:
            if not ui.ask_yes_no('There is no encounter set. Would you like to set it before proceeding?'):
                return
        pc = add_pc(self.session, self.enc)
        if self.enc:
            self.enc.characters[pc.name] = pc

    def do_print_encounter(self, arg):
        print(self.enc)

    def do_set_initiatives(self):
        die = Dice(1, 20)
        for key, item in self.enc.characters.items():
            roll = 0
            while not roll:
                roll = die.check_roll(input("Enter initiative roll for {0}: ".format(key)))
            item.initiative = roll + item.initiative_bonus

        self.enc.init_order = sorted(
            self.enc.characters, key=attrgetter('initiative_bonus', 'initiative'), reverse=True
        )

    # TODO rewrite
    def do_heal(self, creature, health_up):
        # too many different ways to heal to do dice validation here
        if health_up > 0:
            self.enc.characters[creature].heal(health_up)

    # TODO rewrite
    def do_damage(self, creature, health_down):
        # too many different ways to damage to do dice validation here
        # TODO: make generic actors
        if health_down > 0:
            self.enc.characters[creature].heal(health_down)

    # TODO needs work on the status checks and such
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
                self.current_player = self.enc.characters[creature]

                # So what we're saying here is that any creature that drops to 0 health will automatically become
                # unconscious. Then, when they call Character.dead() they will have their status set to DEAD
                # This way we can clean up heros and Monsters alike
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
                if self.current_player.status == Status.ALIVE:
                    self.current_player.do_turn()

    def do_begin_encounter(self, encounter_name=''):
        self.enc = None
        if not encounter_name:
            encounters = [e[0] for e in s.query(Encounter.name).all()]
            if not encounters:
                ui.info(ui.red, 'No encounters in the database. Use load_from_cfg or create_encounter to add data')
                return
            encounter_name = ui.ask_choice('Which encounter would you like to load?', encounters)
        enc = s.query(Encounter).filter_by(name=encounter_name).one_or_none()
        if not enc:
            ui.info(ui.red, 'No encounter by that name found')
            return
        self.enc = enc

    def do_create_encounter(self, arg):
        name = ui.ask_string('Encounter name')
        e = Encounter()
        e.name = name
        s.add(e)
        s.commit()

    def do_load_from_cfg(self, arg):
        pass


if __name__ == '__main__':
    App().cmdloop()
