from .character import Character
from .monster import Monster
from .hero import Hero


class Encounter(object):
    def __init__(self):
        self.monsters = {}
        self.pcs = {}
        self.npcs = {}
        self.monsters = {}

    def add_player(self, name, health, ac, initiative, speed, player):
        player = Hero(name, health, ac, initiative, speed, player)
        self.pcs[name] = player

    def add_monster(self, name, health, ac, initiative, speed, xp):
        monster = Monster(name, health, ac, initiative, speed, xp)
        self.monsters[name] = monster

    def add_npc(self, name, health, ac, initiative, speed):
        npc = Character(name, health, ac, initiative, speed)
        self.npcs[name] = npc
