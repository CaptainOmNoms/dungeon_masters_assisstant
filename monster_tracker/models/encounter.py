from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from monster_tracker.models import Base


class Encounter(Base):
    __tablename__ = 'encounter'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    total_xp = Column(Integer)
    characters = relationship(
        'Character', back_populates='encounter', collection_class=attribute_mapped_collection('name')
    )

    def __repr__(self):
        return '\n'.join(list(map(lambda c: repr(c), self.characters.values())))
        ret = []
        for val in self.characters.values():
            ret += '{}\n'.format(repr(val))
        return ret

    def __init__(self, name=None):
        self.total_xp = 0
        self.init_order = []
        self.name = name
