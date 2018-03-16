from marshmallow_sqlalchemy import ModelSchema
from monster_tracker.models import Encounter


class EncounterSchema(ModelSchema):

    class Meta:
        model = Encounter
