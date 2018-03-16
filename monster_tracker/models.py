# pylint: disable=too-few-public-methods
from enum import IntEnum
from sqlalchemy import Column, Integer, Text, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import attribute_mapped_collection
from .dice import Dice

Base = declarative_base()  # pylint: disable=invalid-name

Status = IntEnum('Status', 'DEAD ALIVE UNCONSCIOUS STABLE')  # pylint: disable=invalid-name


class Character(Base):  # pylint: disable=too-many-instance-attributes
    __tablename__ = 'character'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    max_health = Column(Integer)
    temp_health = Column(Integer)
    current_health = Column(Integer)
    armor_class = Column(Integer)
    initiative_bonus = Column(Integer)
    initiative = Column(Integer)
    speed = Column(Integer)
    type = Column(Text)
    encounter_id = Column(Integer, ForeignKey('encounter.id'))
    encounter = relationship('Encounter', back_populates='characters')

    __mapper_args__ = {'polymorphic_identity': 'character', 'polymorphic_on': type}

    def alive(self):
        return self.health > 0

    def damage(self, dealt_damage, damage_type):
        self.health -= dealt_damage
        if self.health < 0:
            self.health = 0

    def heal(self, healed_damage):
        temp = self.current_health + healed_damage
        maximum = self.current_health + self.temp_health
        if temp <= maximum:
            self.current_health += healed_damage

    def move(self):
        self.moved = True

    def act(self):
        pass

    def bonus(self):
        pass

    def begin_turn(self):
        raise NotImplementedError('No turn for generic character')

    def death(self):
        raise NotImplementedError('No death for generic character')

    def __init__(self, name, health, ac, initiative_bonus, initiative, speed):
        self.name = name
        self.health = health
        self.ac = ac
        self.initiative_bonus = initiative_bonus
        self.initiative = initiative
        self.speed = speed
        self.status = Status.ALIVE
        self.moved = False

    def __repr__(self):
        return '{}, Health: {} Initiative: {} AC: {} Speed: {}'.format(
            self.name, self.health, self.initiative, self.ac, self.speed
        )


class Monster(Character):
    experience = Column(Integer)

    __mapper_args__ = {'polymorphic_identity': 'monster'}

    def death(self):
        return self.experience

    def begin_turn(self):
        pass
        #TODO print available actions, bonus actions, and speed


class Hero(Character):
    player = Column(Text)

    __mapper_args__ = {'polymorphic_identity': 'hero'}

    def death(self):
        die = Dice(1, 20)
        roll = 0
        while not roll:
            roll = die.check_roll(int(input("Enter death save roll for {0}: ".format(self.name))))
        reset = False
        if roll == 1:  # roll a nat 1
            self.death_saves['failed'] += 2
        elif roll < 10:  # rolled 2-9
            self.death_saves['failed'] += 1
        elif roll < 20:  # rolled 11-19
            self.death_saves['saved'] += 1
            if self.death_saves['saved'] == 3:
                reset = True
                self.status = Status.STABLE
        else:  # rolled a nat 20
            self.health = 1
            reset = True
            self.status = Status.ALIVE
        if self.death_saves['failed'] == 3:
            reset = True
            self.status = Status.DEAD
            return True
        if reset:
            self.death_saves['saves'] = 0
            self.death_saves['failed'] = 0
        return False

    # TODO implement this
    def begin_turn(self):
        pass
        #if self.player == 'DM':
            #TODO print available actions, bonus actions, and speed
        #else:
            #await next signal?

    def __init__(self, name, health, ac, initiative_bonus, speed, player='DM'):
        super().__init__(name, health, ac, initiative_bonus, 0, speed)
        self.death_saves = {'failed': 0, 'saved': 0}
        self.player = player

    def __repr__(self):
        return '{}, Health: {} Initiative: {} AC: {} Speed: {}'.format(
            self.name, self.health, self.initiative, self.armor_class, self.speed
        )


class Encounter(Base):
    __tablename__ = 'encounter'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    total_xp = Column(Integer)
    characters = relationship(
        'Character', back_populates='encounter', collection_class=attribute_mapped_collection('name')
    )

    def deal_damage(self, done_by, done_to, amount, damage_type):
        done_to.damage(amount, damage_type)
        if done_to.current_health == 0:
            if isinstance(done_to, Monster):
                self.total_xp += done_to.experience
        #TODO add damage to done_by's damage quanity tracker
        #TODO if done_to.status == dead && done_to is monster add xp to encounter.total_xp

    def __repr__(self):
        ret = ''
        for val in self.creatures.values():
            ret += repr(val)
        return ret

    def __init__(self):
        self.total_xp = 0


def create_session(uri):
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


s = create_session('sqlite:///:memory:')()  # pylint: disable=invalid-name
