from marshmallow_sqlalchemy import ModelSchema
from monster_tracker.models import Monster, Character
from monster_tracker.character import CharacterOld

#class MonsterSchema(ModelSchema):
#    class Meta:
#        model = Monster


class MonsterOld(CharacterOld):
    """
    Any NPC
    """

    # TODO Is this docstring accurate?
    def __init__(self, name, health, ac, initiative_bonus, speed, xp):
        super().__init__(name, health, ac, initiative_bonus, 0, speed)
        self.xp = xp
        # TODO is alive the right word for this. Should there be a marker for being undead?
        self.alive = True


# TODO create lookup function
# TODO database
