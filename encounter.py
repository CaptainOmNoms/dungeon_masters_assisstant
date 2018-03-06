from marshmallow_sqlalchemy import ModelSchema
from .models import Encounter, Character, Monster, Hero


class EncounterSchema(ModelSchema):
    class Meta:
        model = Encounter


class EncounterOld(object):
    def __init__(self):
        self.creatures = {}

    def add_player(self, name, health, ac, initiative, speed, played_by):
        player = Hero(name, health, ac, initiative, speed, played_by)
        self.creatures[name] = player

    def add_monster(self, name, health, ac, initiative, speed, xp):
        monster = Monster(name, health, ac, initiative, speed, xp)
        self.creatures[name] = monster

    def add_npc(self, name, health, ac, initiative, speed):
        npc = Hero(name, health, ac, initiative, speed, '')
        self.creatures[name] = npc
