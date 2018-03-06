from marshmallow_sqlalchemy import ModelSchema
from .character import Character
from .monster import Monster
from .hero import Hero
from .models import Encounter


class EncounterSchema(ModelSchema):
    class Meta:
        model = Encounter


class EncounterOld(object):
    def __init__(self):
        self.creatures = {}
        self.total_xp = 0
        self.current_player = Character()

    def add_player(self, name, health, ac, initiative_bonus, speed, played_by):
        player = Hero(name, health, ac, initiative_bonus, speed, played_by)
        self.creatures[name] = player

    def add_monster(self, name, health, ac, initiative_bonus, speed, xp):
        monster = Monster(name, health, ac, initiative_bonus, speed, xp)
        self.creatures[name] = monster

    def add_npc(self, name, health, ac, initiative, speed):
        npc = Hero(name, health, ac, initiative, speed, '')
        self.creatures[name] = npc

    def deal_damage(self, done_by, done_to, amount, type):
        done_to.damage(amount)

        #TODO add damage to done_by's damage quanity tracker
        #TODO if done_to.status == dead && done_to is monster add xp to encounter.total_xp

    def print(self): #print whole encounter
        for key, item in self.creatures.items():
            print("{0}, {1} AC: {2} Health: {3}".format(item.name, item.status, item.ac, item.health))
