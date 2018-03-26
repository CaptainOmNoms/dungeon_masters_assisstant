from sqlalchemy import Column, Text
from sqlalchemy.orm import reconstructor

from monster_tracker.dice import Dice
from monster_tracker.models import Status
from monster_tracker.models.characters import Character


class Hero(Character):
    player = Column(Text, default='DM')

    __mapper_args__ = {'polymorphic_identity': 'hero'}

    def death(self):
        die = Dice(1, 20)
        roll = 0
        while not roll:
            roll = die.check_roll(int(input("Enter death save roll for {0}: ".format(self.name))))
        reset = False
        ret = False
        if roll == 1:  # roll a nat 1
            self.death_saves['failed'] += 2
        elif roll < 10:  # rolled 2-9
            self.death_saves['failed'] += 1
        elif roll < 20:  # rolled 11-19
            self.death_saves['saved'] += 1
            if self.death_saves['saved'] == 3:
                reset = True
                self.status = Status.STABLE
        else:  # rolled a nat 20
            self.current_health = 1
            reset = True
            self.status = Status.ALIVE
        if self.death_saves['failed'] == 3:
            reset = True
            self.status = Status.DEAD
            ret = True
        if reset:
            self.death_saves['saves'] = 0
            self.death_saves['failed'] = 0
        return ret

    def damage(self, dealt_damage):
        if self.status == Status.STABLE:
            self.status = Status.UNCONSCIOUS
        elif self.status == Status.UNCONSCIOUS:
            self.death_saves['failed'] += 1
        else:
            self.current_health -= dealt_damage
            self.temp_health -= dealt_damage
            if self.temp_health < 0:
                self.temp_health = 0
            if self.current_health <= 0:
                if abs(self.current_health) >= self.max_health:
                    self.status = Status.DEAD
                    self.current_health = 0
                else:
                    self.status = Status.UNCONSCIOUS
                    self.current_health = 0

    def heal(self, healed_damage):
        if self.status != Status.DEAD:
            self.current_health += healed_damage
            if self.current_health > self.max_health + self.temp_health:
                self.current_health = self.max_health + self.temp_health
            if self.status != Status.ALIVE:
                self.status = Status.ALIVE
            self.death_saves['failed'] = 0
            self.death_saves['saved'] = 0

    def add_temp_health(self, temp_health):
        self.current_health += temp_health
        self.temp_health += temp_health

    # TODO implement this
    def turn(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.death_saves = {'failed': 0, 'saved': 0}

    @reconstructor
    def reconstruct(self):
        self.death_saves = {'failed': 0, 'saved': 0}

    def __repr__(self):
        return (f'{self.name}, Health: {self.current_health} Initiative: {self.initiative} AC: {self.armor_class}' +
                'Speed: {self.speed}')
