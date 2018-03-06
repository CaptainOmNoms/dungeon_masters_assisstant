from enum import IntEnum
from marshmallow_sqlalchemy import ModelSchema
from monster_tracker.models import Character

#class CharacterSchema(ModelSchema):
#    class Meta:
#        model = Character
Status = IntEnum('Status', 'DEAD ALIVE UNCONSCIOUS STABLE')


class CharacterOld(object):
    """Any PC or NPC in an encounter"""

    def __init__(self, name, health, ac, initiative_bonus, initiative, speed):
        self.name = name
        self.health = health
        self.ac = ac
        self.initiative_bonus = initiative_bonus
        self.initiative = initiative
        self.speed = speed
        self.status = Status.ALIVE
        self.moved = False

    def damage(self, damage, type):
        # check if self is resistant to type damage
        # TODO this could get tricky with rage abilities
        #if resistant:
        #    damage = damage / 2
        #check if char is vulnerabe to type damage
        #if vulnerabe:
        #    damage = damage * 2
        self.health -= damage
        if self.health <= 0:
            self.health = 0

    def heal(self, heal):
        self.health += heal

    #def print(self):
    #    print("{0}, Health: {1} Initiative: {2} AC: {3} Speed: {4}".format(self.name, self.health, self.initiative, self.ac, self.speed))
    # TODO add attacks print out
    # TODO repr

    def __repr__(self):
        return '{}, Health: {} Initiative: {} AC: {} Speed: {}'.format(
            self.name, self.health, self.initiative, self.ac, self.speed)

    def do_action(self):
        pass

    def do_bonus(self):
        pass

    def do_move(self):
        self.moved = True

    def begin_turn(self):
        raise NotImplementedError('No turn for generic character')

    def death(self):
        raise NotImplementedError('No death for generic character')
