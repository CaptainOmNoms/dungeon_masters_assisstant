# pylint: disable=too-few-public-methods
from marshmallow_sqlalchemy import ModelSchema
from monster_tracker.models import Hero


class HeroSchema(ModelSchema):

    class Meta:
        model = Hero
