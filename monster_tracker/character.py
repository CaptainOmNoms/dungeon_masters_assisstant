from enum import IntEnum
from marshmallow_sqlalchemy import ModelSchema
from monster_tracker.models import Character


class CharacterSchema(ModelSchema):

    class Meta:
        model = Character


Status = IntEnum('Status', 'DEAD ALIVE UNCONSCIOUS STABLE')
