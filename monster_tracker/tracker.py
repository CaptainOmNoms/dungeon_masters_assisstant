import re
from copy import deepcopy
from itertools import cycle, chain
from operator import attrgetter
from pathlib import Path
from typing import Any, Callable, List, Tuple

import tabulate
import ui
import yaml
from cmd2 import Cmd
from more_itertools import peekable, consume

from monster_tracker.dice import Dice
from monster_tracker.models import Encounter, Character, Monster, Hero, s, Status


def add_npc(sess, enc: Encounter, name: str, health: int, ac: int, init_bon: int, speed: str) -> Hero:
    npc = Hero(name, health, ac, init_bon, speed)
    sess.add(npc)
    npc.encounter_id = enc.id
    sess.commit()
    return npc


def add_pc(sess, enc: Encounter, name: str, health: int, ac: int, init_bon: int, speed: int, player: str) -> Hero:
    pc = Hero(name, health, ac, init_bon, speed, player)
    pc.encounter_id = enc.id
    sess.add(pc)
    sess.commit()
    return pc


def get_input(
    query_string: str = None,
    choices: List = None,
    out_type: type = str,
    conditions: Tuple[Callable[..., Any], str] = None  # pylint: disable=bad-whitespace
) -> Any:
    """
    Gets user input and coerces it into the type provided.
    Note that query_string can be a format string and will be evaluated before this function is entered
    function, when the calling variables are out of scope
    If nothing is entered, we will keep looping. If the user wants to stop entering data, they can enter 'quit'
    """
    while True:
        if not choices:
            user_data = ui.ask_string(query_string) if query_string else ui.read_input()
        else:
            user_data = ui.ask_choice(query_string or '', deepcopy(choices))
        if not user_data:
            ui.error('Nothing entered')
            continue
        if user_data.lower() == 'quit':
            raise ValueError
        try:
            typed_data = out_type(user_data)


# So ideally what we could do here is make a parser class (maybe just use marshmallow) to parse the data instead?
        except (TypeError, ValueError):
            ui.error(f'Unable to coerce string into {out_type}')
            continue
        if conditions:
            if not conditions[0](typed_data):
                ui.error(conditions[1])
                continue
        return typed_data


class App(Cmd):

    def __init__(self) -> None:
        super().__init__()
        self.enc = Encounter()
        self.current_player = Character()
        self.session = s

    def do_add_npc(self, _) -> None:
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

    def do_add_pc(self, _) -> None:
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

    def do_print_encounter(self, _) -> None:
        print('\033[H\033[J')
        print(f'\nEncounter: {self.enc.name}\n{"-" * (10 + len(self.enc.name))}\n')
        print(
            tabulate.tabulate(
                map(lambda c: self.enc.characters[c].to_tuple(), self.enc.init_order),
                headers=['Name', 'HP', 'AC', 'Initiative', 'Movement', 'Status'],
                stralign='right'
            )
        )
        print('\n')

    def do_set_initiatives(self, _) -> None:
        die = Dice(1, 20)
        for key, item in self.enc.characters.items():
            roll = 0
            while not roll:
                roll = die.check_roll(int(input(f"Enter initiative roll for {key}: ")))
            item.initiative = roll + item.initiative_bonus
        self.enc.init_order = list(
            map(
                attrgetter('name'),
                sorted(self.enc.characters.values(), key=attrgetter('initiative', 'initiative_bonus'), reverse=True)
            )
        )
        ui.info(ui.red, 'Initiative order has been set.')
        input()

    def do_heal(self, _) -> None:
        try:
            target = get_input('Who is being healed', choices=self.enc.init_order)
            health_up = get_input(
                query_string='How much is being healed',
                out_type=int,
                conditions=(lambda x: x > 0, 'No null or negative healing')
            )
            self.enc.characters[target].heal(health_up)
        except ValueError:
            return

    # TODO make generic actors
    def do_damage(self, target: str, health_down: int) -> None:
        if health_down > 0:
            self.enc.characters[target].damage(health_down)
        else:
            ui.info(ui.red, 'You must do positive damage')

    def do_attack(self, _) -> None:
        damage = 0
        try:
            target = get_input('Who are you attacking?', choices=self.enc.init_order)
            damage = get_input(
                query_string='How much damage',
                out_type=int,
                conditions=(lambda x: x > 0, 'You must do positive damage')
            )
            self.do_damage(target, damage)
        except ValueError:
            return

    def do_health_adjust(self, creature: str, health: int) -> None:
        self.enc.characters[creature].adjust_max_health(health)

    # TODO needs work on the status checks and such
    def do_encounter(self, _) -> None:
        self.do_print_encounter(_)
        self.do_set_initiatives(_)
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
                        print(f'{self.current_player.name} is stable and must be healed to take turn')
                        input()
                    if self.current_player.status == Status.ALIVE:
                        options = ['Quit', 'Attack', 'Heal', 'Move']
                        task = None
                        while task != 'Quit':
                            task = ui.ask_choice(f'What would {self.current_player.name} like to do?', options)
                            if task == 'Move':
                                try:
                                    distance = get_input(
                                        query_string='How far are you moving',
                                        out_type=int,
                                        conditions=(lambda x: x >= 0, 'You cannot move negative feet')
                                    )
                                    self.enc.characters[self.current_player.name].move(distance)
                                except ValueError:
                                    continue
                            elif task == 'Attack':
                                self.do_attack(_)
                            elif task == 'Heal':
                                self.do_heal(_)
                            elif task == 'Quit':
                                ui.info(ui.red, f'{self.current_player.name} has ended their turn')

    def do_begin_encounter(self, encounter_name: str = '') -> None:
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
        print(f'Encounter {encounter_name} begun')
        self.enc = enc
        self.do_encounter('')

    def do_create_encounter(self, _) -> None:
        name = ui.ask_string('Encounter name')
        enc = Encounter()
        enc.name = name
        s.add(enc)
        s.commit()

    def do_load_from_cfg(self, _) -> None:
        same_dir = Path('.').glob('*.yaml')
        data_dir = Path(__file__).parent.joinpath('data').glob('*.yaml')

        name_pairs = {re.sub('.yaml', '', f.name): f for f in chain(same_dir, data_dir)}
        f_name = ui.ask_choice(
            'Which YAML file would you like to load? Press <ENTER> to enter your own file path',
            list(name_pairs.keys())
        )
        f_path = name_pairs.get(f_name)

        while not f_name:
            prompt = """Please enter the full file path to the YAML file you would like to load.
Press <ENTER> to stop loading a YAML file."""

            try:
                f_name = get_input(query_string=prompt)
            except ValueError:
                return
            f_path = Path(f_name)
            if not f_path.exists():
                ui.error('Path does not exist')
                f_name = None

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
        ui.info(f'Encounter {enc.name} loaded')
        self.do_begin_encounter(enc.name)


if __name__ == '__main__':
    App().cmdloop()
