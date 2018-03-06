from marshmallow_sqlalchemy import ModelSchema
from .models import Character
from enum import Enum


class CharacterSchema(ModelSchema):
    class Meta:
        model = Character


class CharacterOld(object):
    """Any PC or NPC in an encounter"""

    def __init__(self, name, health, ac, initiative_bonus, initiative, speed):
        self.name = name
        self.health = health
        self.ac = ac
        self.initiative_bonus = initiative_bonus
        self.initiative = initiative
        self.speed = speed
        self.status = 'alive' # convert to enum
        self.moved = False

    def damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0

    def heal(self, heal):
        self.health += heal

    def print(self):
        print("{0}, Health: {1} Initiative: {2} AC: {3} Speed: {4}".format(self.name, self.health, self.initiative, self.ac, self.speed))
        # TODO add attacks print out
        # TODO repr

    def do_action(self):
        pass

    def do_bonus(self):
        pass

    def do_move(self):
        self.moved = True

    def begin_turn(self):
        raise NotImplemented('No turn for generic character')


    def death(self):
        raise NotImplemented('No death for generic character')
