# pylint: disable=too-few-public-methods
from marshmallow_sqlalchemy import ModelSchema
from monster_tracker.character import CharacterOld, Status
from monster_tracker.models import Hero
from monster_tracker.dice import Dice


class HeroSchema(ModelSchema):

    class Meta:
        model = Hero


class HeroOld(CharacterOld):

    def __init__(self, name, health, ac, initiative_bonus, speed, player):
        super().__init__(name, health, ac, initiative_bonus, 0, speed)
        self.death_saves = {'failed': 0, 'saved': 0}
        if player != '':
            self.player = player
        else:
            self.player = 'DM'

    def death(self):
        die = Dice(1, 20)
        roll = 0
        while not roll:
            roll = die.check_roll(int(input("Enter death save roll for {0}: ".format(self.name))))
        if roll == 1:  # roll a nat 1
            self.death_saves['failed'] += 2
            if self.death_saves['failed'] == 3:
                self.death_saves['saves'] = 0
                self.death_saves['failed'] = 0
                self.status = Status.DEAD
        elif roll < 10:  # rolled 2-9
            self.death_saves['failed'] += 1
            if self.death_saves['failed'] == 3:
                self.death_saves['saves'] = 0
                self.death_saves['failed'] = 0
                self.status = Status.DEAD
        elif roll < 20:  # rolled 11-19
            self.death_saves['saved'] += 1
            if self.death_saves['saved'] == 3:
                self.death_saves['saves'] = 0
                self.death_saves['failed'] = 0
                self.status = Status.STABLE
        else:  # rolled a nat 20
            self.health = 1
            self.death_saves['saves'] = 0
            self.death_saves['failed'] = 0
            self.status = 'alive'

    # TODO implement this
    def begin_turn(self):
        pass
