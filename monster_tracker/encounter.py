from marshmallow_sqlalchemy import ModelSchema
from monster_tracker.models import Encounter, Character, Monster, Hero
from monster_tracker.hero import HeroOld
from monster_tracker.monster import MonsterOld


class EncounterSchema(ModelSchema):
    class Meta:
        model = Encounter


class EncounterOld(object):
    def __init__(self):
        self.creatures = {}
        self.total_xp = 0
        self.current_player = Character()


    def add_player(self, name, health, ac, initiative_bonus, speed, played_by):
        player = HeroOld(name, health, ac, initiative_bonus, speed, played_by)
        self.creatures[name] = player

    def add_monster(self, name, health, ac, initiative_bonus, speed, xp):
        monster = MonsterOld(name, health, ac, initiative_bonus, speed, xp)
        self.creatures[name] = monster

    def add_npc(self, name, health, ac, initiative, speed):
        npc = HeroOld(name, health, ac, initiative, speed, '')
        self.creatures[name] = npc

    def deal_damage(self, done_by, done_to, amount, type):
        done_to.damage(amount)

        #TODO add damage to done_by's damage quanity tracker
        #TODO if done_to.status == dead && done_to is monster add xp to encounter.total_xp

    def __repr__(self):
        ret = ''
        for val in self.creatures.values():
            ret += repr(val)
            #ret += "{}, {} AC: {} Health: {}\n".format(val.name, val.status, val.ac, val.health)
        return ret

    #def print(self): #print whole encounter
    #    for key, item in self.creatures.items():
    #        print("{0}, {1} AC: {2} Health: {3}".format(item.name, item.status, item.ac, item.health))
