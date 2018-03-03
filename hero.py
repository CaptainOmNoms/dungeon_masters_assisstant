from marshmallow_sqlalchemy import ModelSchema
from .character import Character
from .models import Hero


class HeroSchema(ModelSchema):
    class Meta:
        model = Hero


class HeroOld(Character):
    def __init__(self, name, health, ac, initiative, speed, player):
        super().__init__(name, health, ac, initiative, speed)
        if player != '':
            self.player = player
        else:
            self.player = 'DM'

