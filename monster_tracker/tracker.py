from itertools import cycle, chain
from operator import attrgetter
from pathlib import Path
import re
from cmd2 import Cmd
from more_itertools import peekable, consume
import ui
import tabulate
import yaml
from monster_tracker.dice import Dice
from monster_tracker.models import Encounter, Monster, Hero, s, Status


def add_npc(s, enc, name, health, ac, init_bon, speed):
    npc = Hero(name, health, ac, init_bon, speed)
    s.add(npc)
    npc.encounter_id = enc.id
    s.commit()
    return npc

def add_pc(s, enc, name, health,ac, init_bon, speed, player):
    pc = Hero(name, health, ac, init_bon, speed, player)
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
        # self.enc.init_order = []

    def do_hello(self, arg):
        print('Hello world')

    def do_add_npc(self, _):
        if not self.enc:
            if not ui.ask_yes_no('There is no encounter set. Would you like to set it before proceeding?'):
                return

        name = ui.ask_string('Name')
        health = ui.ask_string('Health')
        ac = ui.ask_string('AC')
        ib = ui.ask_string('Initiative Bonus')
        speed = ui.ask_string('Speed')
        npc = add_npc(self.session, self.enc, name, health, ac, ib, speed)
        if self.enc:
            self.enc.characters[npc.name] = npc

    def do_add_pc(self, _):
        if not self.enc:
            if not ui.ask_yes_no('There is no encounter set. Would you like to set it before proceeding?'):
                return

        name = ui.ask_string('Name')
        health = ui.ask_string('Health')
        ac = ui.ask_string('AC')
        ib = ui.ask_string('Initiative Bonus')
        speed = ui.ask_string('Speed')
        player = ui.ask_string('Player')
        pc = add_pc(self.session, self.enc, name, health, ac, ib, speed, player)
        if self.enc:
            self.enc.characters[pc.name] = pc

    def do_print_encounter(self, _):
        print('\nEncounter {}\n{}\n'.format(self.enc.name, '-' * (10+len(self.enc.name))))
        print(tabulate.tabulate(
            map(lambda x: x.to_tuple(), self.enc.characters.values()),
            headers=['Name', 'Current HP', 'AC', 'Initiative', 'speed', 'Max HP', 'Temp HP']))

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
                if isinstance(self.current_player, Hero):
                    if self.current_player.status == Status.UNCONSCIOUS:
                        if self.current_player.dead():
                            self.enc.init_order.remove(creature)
                            # By breaking here, we exit the for loop
                            # This will cause a recomputation of the circular list
                            # We then get the next item in the list
                            next_char = self.enc.init_order.index(init_order.peek())
                            break
                if self.current_player.status == Status.ALIVE:
                    self.current_player.do_turn()
                if isinstance(self.current_player, Monster):
                    self.enc.total_xp += self.current_player.experience

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
        enc = Encounter()
        enc.name = name
        s.add(enc)
        s.commit()

    def do_load_from_cfg(self, arg):
        same_dir = Path('.').glob('*.yaml')
        data_dir = Path(__file__).parent.joinpath('data').glob('*.yaml')

        name_pairs = {re.sub('.yaml', '', f.name): f for f in chain(same_dir, data_dir)}
        f_name = ui.ask_choice(
            'Which YAML file would you like to load? Press <ENTER> to enter your own file path',
            list(name_pairs.keys()))

        f_path = name_pairs.get(f_name)

        while not f_name:
            f_name = ui.ask_string('Please enter the full file path to the YAML file you would like to load. Press <ENTER> to stop loading a YAML file.')
            if not f_name:
                return
            f_path = Path(f_name)
            if not f_path.exists():
                ui.error('Path does not exist')

        with f_path.open() as f:
            encounter = yaml.load(f)

        for e in encounter:
            chars = e.pop('characters') if 'characters' in e else []
            enc = Encounter(**e)
            s.add(enc)
            s.commit()
            for character in chars:
                if 'player' in character:
                    c = Hero(**character)
                else:
                    c = Monster(**character)
                enc.characters[c.name] = c
            s.commit()
        ui.info('Encounter {} loaded'.format(enc.name))


if __name__ == '__main__':
    App().cmdloop()
