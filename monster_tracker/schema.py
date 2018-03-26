from copy import deepcopy
from apistar import typesystem
import typing


class GreaterThanZero(typesystem.Integer):
    minimum = 0
    description = 'Greater than zero'


def greaterthanzero(**kwargs) -> typing.Type:
    return type('GreaterThanZero', (GreaterThanZero,), kwargs)


class Character(typesystem.Object):
    properties = {
        'name': typesystem.string(description='The name of the character'),
        'max_health': greaterthanzero(description='Maximum health'),
        'temp_health': typesystem.integer(description='Temporary health'),
        'armor_class': greaterthanzero(description='How hard it is to hit this character'),
        'initiative_bonus': typesystem.integer(description='Bonus to character\'s initiative'),
        'initiative': typesystem.integer(description='How quick and speedy a character is'),
        'speed': typesystem.integer(description='How far a character can move per turn'),
    }


class Monster(Character):
    properties = deepcopy(Character.properties)
    properties.update({
        'experience': typesystem.integer(description='How much experience this monster is worth')
    })


class Hero(Character):
    properties = deepcopy(Character.properties)
    properties.update({
        'player': typesystem.string(description='The person playing this character')
    })


class HeroRepr(Hero):
    properties = deepcopy(Hero.properties)
    del properties['max_health']
    del properties['temp_health']
    del properties['initiative_bonus']
    del properties['player']


class MonsterRepr(Monster):
    properties = deepcopy(Monster.properties)
    del properties['max_health']
    del properties['temp_health']
    del properties['initiative_bonus']
    del properties['experience']
