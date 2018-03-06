from sqlalchemy import Column, Integer, Text, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base, ConcreteBase

Base = declarative_base()


class Character(Base, ConcreteBase):
    __tablename__ = 'character'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    health = Column(Integer)
    armor_class = Column(Integer)
    initiative = Column(Integer)
    speed = Column(Integer)
    type = Column(Text)
    encounter_id = Column(Integer, ForeignKey('encounter.id'))
    encounter = relationship('Encounter', back_populates='')

    __mapper_args__ = {
        'polymorphic_identity': 'character',
        'polymorphic_on': 'type'
    }

    def alive(self):
        return self.health > 0


class Monster(Character):
    # __tablename__ = 'monster'
    experience = Column(Integer)

    __mapper_args__ = {'polymorphic_identity': 'monster'}


class Hero(Character):
    # __tablename__ = 'hero'
    player = Column(Text)
    __mapper_args__ = {'polymorphic_identity': 'hero'}

    def __repr__(self):
        return '{}, Health: {} Initiative: {} AC: {} Speed: {}'.format(
            self.name, self.health, self.initiative, self.armor_class,
            self.speed)


class Encounter(Base):
    __tablename__ = 'encounter'
    id = Column(Integer, primary_key=True)
    # characters = relationship('character', secondary=encounter_characters)
    characters = relationship('Character', back_populates='encounter')


def create_session(uri):
    engine = create_engine(uri)
    return sessionmaker(bind=engine)


s = create_session('sqlite:///:memory:')()
