# pylint disable=too-few-public-methods
from marshmallow_sqlalchemy import ModelSchema
from monster_tracker.models import Monster


class MonsterSchema(ModelSchema):

    class Meta:
        model = Monster
