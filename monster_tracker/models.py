# pylint: disable=too-few-public-methods
from enum import IntEnum

from sqlalchemy import Column, Integer, Text, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from .dice import Dice

Base = declarative_base()  # pylint: disable=invalid-name

Status = IntEnum('Status', 'DEAD ALIVE UNCONSCIOUS STABLE')  # pylint: disable=invalid-name

# So I think we should store the normal attributes for a monster
# Then when the DM looks it up, they have the option to edit any attributes they need to
# And a copy of that monster gets created with the name they specify
# That way there can always be one source of monster data but a bunch of different monsters
# Maybe we need a monster template class?


class Character(Base):  # pylint: disable=too-many-instance-attributes
    __tablename__ = 'character'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    max_health = Column(Integer)
    temp_health = Column(Integer)
    current_health = Column(Integer)
    armor_class = Column(Integer)
    initiative_bonus = Column(Integer)
    initiative = Column(Integer)
    speed = Column(Integer)
    movement = Column(Integer)
    status = Column(Integer)
    type = Column(Text)
    encounter_id = Column(Integer, ForeignKey('encounter.id'))
    encounter = relationship('Encounter', back_populates='characters')

    __mapper_args__ = {'polymorphic_identity': 'character', 'polymorphic_on': type}

    def to_tuple(self):
        return (self.name, self.current_health, self.armor_class, self.initiative, self.speed)

    def alive(self):
        return self.current_health > 0

    def damage(self, dealt_damage):
        raise NotImplementedError('No death for generic character')

    def heal(self, healed_damage):
        self.current_health += healed_damage
        if self.current_health > self.max_health + self.temp_health:
            self.current_health = self.max_health + self.temp_health

    def adjust_max_health(self, health):
        self.max_health += health
        self.current_health += health

    def move(self, feet):
        if self.movement > 0:
            self.movement -= feet
        else:
            print('{} has already moved their full movement'.format(self.name))

    def act(self):
        pass

    def bonus(self):
        pass

    def turn(self):
        raise NotImplementedError('No turn for generic character')

    def death(self):
        raise NotImplementedError('No death for generic character')

    def __init__(
        self,
        name=None,
        max_health=None,
        ac=None,
        initiative_bonus=0,
        initiative=0,
        speed=None,
        temp_health=0,
        current_health=None
    ):
        self.name = name
        self.armor_class = ac
        self.initiative_bonus = initiative_bonus
        self.initiative = initiative
        self.speed = speed
        self.status = Status.ALIVE
        self.max_health = max_health
        self.temp_health = temp_health
        self.current_health = current_health or self.max_health
        self.movement = speed

    def __repr__(self):
        return '{}, Health: {} Initiative: {} AC: {} Speed: {}'.format(
            self.name, self.current_health, self.initiative, self.ac, self.speed
        )


class Monster(Character):
    experience = Column(Integer)

    __mapper_args__ = {'polymorphic_identity': 'monster'}

    def death(self):
        return self.experience

    def damage(self, dealt_damage):
        self.current_health -= dealt_damage
        self.temp_health -= dealt_damage
        if self.temp_health < 0:
            self.temp_health = 0
        if self.current_health <= 0:
            self.status = Status.DEAD
            self.current_health = 0

    def turn(self):
        print('DM do your shit')
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
        ret = False
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
            self.current_health = 1
            reset = True
            self.status = Status.ALIVE
        if self.death_saves['failed'] == 3:
            reset = True
            self.status = Status.DEAD
            ret = True
        if reset:
            self.death_saves['saves'] = 0
            self.death_saves['failed'] = 0
        return ret

    def damage(self, dealt_damage):
        if self.status == Status.STABLE:
            self.status = Status.UNCONSCIOUS
        elif self.status == Status.UNCONSCIOUS:
            self.death_saves['failed'] += 1
        else:
            self.current_health -= dealt_damage
            self.temp_health -= dealt_damage
            if self.temp_health < 0:
                self.temp_health = 0
            if self.current_health <= 0:
                if self.current_health == -self.max_health:
                    self.status = Status.DEAD
                else:
                    self.status = Status.UNCONSCIOUS
                    self.current_health = 0

    # TODO implement this
    def turn(self):
        pass

    def __init__(
        self,
        name=None,
        max_health=None,
        ac=None,
        initiative_bonus=0,
        speed=0,
        player='DM',
        current_health=0,
        temp_health=0
    ):
        super().__init__(
            name=name,
            ac=ac,
            initiative_bonus=initiative_bonus,
            initiative=0,
            speed=speed,
            current_health=current_health,
            temp_health=temp_health,
            max_health=max_health
        )
        self.death_saves = {'failed': 0, 'saved': 0}
        self.player = player

    def __repr__(self):
        return '{}, Health: {} Initiative: {} AC: {} Speed: {}'.format(
            self.name, self.current_health, self.initiative, self.armor_class, self.speed
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
        return '\n'.join(list(map(lambda c: repr(c), self.characters.values())))
        ret = []
        for val in self.characters.values():
            ret += '{}\n'.format(repr(val))
        return ret

    def __init__(self, name=None):
        self.total_xp = 0
        self.init_order = []
        self.name = name


def create_session(uri):
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


s = create_session('sqlite:///:memory:')()  # pylint: disable=invalid-name
