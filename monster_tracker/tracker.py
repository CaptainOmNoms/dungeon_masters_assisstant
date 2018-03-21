import os
import re
from itertools import cycle, chain
from operator import attrgetter
from pathlib import Path

import tabulate
import ui
import yaml
from cmd2 import Cmd
from more_itertools import peekable, consume

from monster_tracker.dice import Dice
from monster_tracker.models import Encounter, Character, Monster, Hero, s, Status


def add_npc(s, enc, name, health, ac, init_bon, speed):
    npc = Hero(name, health, ac, init_bon, speed)
    s.add(npc)
    npc.encounter_id = enc.id
    s.commit()
    return npc


def add_pc(s, enc, name, health, ac, init_bon, speed, player):
    pc = Hero(name, health, ac, init_bon, speed, player)
    pc.encounter_id = enc.id
    s.add(pc)
    s.commit()
    return pc


class App(Cmd):

    def __init__(self):
        super().__init__()
        self.enc = Encounter()
        self.current_player = Character()
        self.session = s
        # self.enc.init_order = []

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
        os.system('cls')
        print('\nEncounter: {}\n{}\n'.format(self.enc.name, '-' * (10 + len(self.enc.name))))
        print(
            tabulate.tabulate(
                map(lambda c: self.enc.characters[c].to_tuple(), self.enc.init_order),
                headers=['Name', 'HP', 'AC', 'Initiative', 'Movement'],
                stralign='right'
            )
        )
        print()
        print()

    def do_print_init_order(self, _):
        os.system('cls')
        print('Initiative Order')
        print('----------------')
        for name in self.enc.init_order:
            print(name)
        print()
        print()

    def do_set_initiatives(self):
        die = Dice(1, 20)
        for key, item in self.enc.characters.items():
            roll = 0
            while not roll:
                roll = die.check_roll(int(input("Enter initiative roll for {0}: ".format(key))))
            item.initiative = roll + item.initiative_bonus
        temp = sorted(self.enc.characters.values(), key=attrgetter('initiative', 'initiative_bonus'), reverse=True)
        for char in temp:
            self.enc.init_order.append(char.name)
        ui.info(ui.red, 'Initiative order has been set. To print the initiative order at any time enter i')

    def do_heal(self):
        target = ui.ask_string('Who is being healed')
        health_up = 0
        while not health_up:
            health_up = int(ui.ask_string('How much is being healed'))
            if health_up > 0:
                self.enc.characters[target].heal(health_up)
            else:
                health_up = 0
                ui.info(ui.red, 'Must heal for more than 0')

    # TODO make generic actors
    def do_damage(self, target, health_down):
        if health_down > 0:
            self.enc.characters[target].damage(health_down)
        else:
            ui.info(ui.red, 'You must do positive damage')

    def do_attack(self):
        target = None
        damage = 0
        # TODO make a ui.ask_choice?
        while target not in self.enc.init_order:
            target = ui.ask_string('Who are you attacking')
        while not damage:
            damage = int(ui.ask_string('How much damage'))
        self.do_damage(target, damage)

    def do_health_adjust(self, creature, health):
        self.enc.characters[creature].adjust_max_health(health)

    # TODO needs work on the status checks and such
    def do_encounter(self, arg):
        self.do_print_encounter('')
        self.do_set_initiatives()
        self.do_print_init_order('')
        next_char = None
        while True:
            init_order = peekable(cycle(self.enc.init_order))
            if next_char:
                consume(init_order, next_char)
                next_char = None
            for creature in init_order:
                self.do_print_encounter('')
                # do setup things for each turn here
                self.current_player = self.enc.characters[creature]
                if isinstance(self.current_player, Monster):
                    if self.current_player.status == Status.DEAD:
                        self.enc.total_xp += self.current_player.death()
                        self.enc.init_order.remove(creature)
                        next_char = self.enc.init_order.index(init_order.peek())
                        break
                    else:
                        self.current_player.turn()
                        input()
                else:
                    if self.current_player.status == Status.UNCONSCIOUS:
                        if self.current_player.death():
                            self.enc.init_order.remove(creature)
                            next_char = self.enc.init_order.index(init_order.peek())
                            break
                    elif self.current_player.status == Status.DEAD:
                        self.enc.init_order.remove(creature)
                        next_char = self.enc.init_order.index(init_order.peek())
                        break
                    elif self.current_player.status == Status.STABLE:
                        print('{} is stable and must be healed to take turn'.format(self.current_player.name))
                        input()
                    if self.current_player.status == Status.ALIVE:
                        task = ui.ask_string(
                            'What would {} like to do? (Move:m , Attack:a, Heal:h or Done:d)'.format(
                                self.current_player.name
                            )
                        )
                        while task != 'd':
                            if task == 'm':
                                num = int(ui.ask_string('How far are you moving'))
                                self.enc.characters[self.current_player.name].move(num)
                            elif task == 'a':
                                self.do_attack()
                            elif task == 'h':
                                self.do_heal()
                            elif task == 'i':
                                self.do_print_init_order('')
                                ui.info(ui.red, 'Current Turn: {}'.format(self.current_player.name))
                            elif task == 'e':
                                self.do_print_encounter('')
                            elif task == 'd':
                                ui.info(ui.red, '{} has ended their turn'.format(self.current_player.name))
                            else:
                                ui.info(ui.red, 'Opps thats not an option. Try again')
                            task = ui.ask_string(
                                'What would {} like to do? (Move:m , Attack:a or done:d)'.format(
                                    self.current_player.name
                                )
                            )

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
        print('Encounter {} begun'.format(encounter_name))
        self.enc = enc
        self.do_encounter('')

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
            list(name_pairs.keys())
        )
        f_path = name_pairs.get(f_name)

        while not f_name:
            f_name = ui.ask_string(
                'Please enter the full file path to the YAML file you would like to load. Press <ENTER> to stop loading a YAML file.'
            )
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
        self.do_begin_encounter(enc.name)


if __name__ == '__main__':
    App().cmdloop()
