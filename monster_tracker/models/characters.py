from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from monster_tracker.models import Base, Status


class Character(Base):  # pylint: disable=too-many-instance-attributes
    __tablename__ = 'character'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    type = Column(Text)
    subtype = Column(Text)
    alignment = Column(Text)
    max_health = Column(Integer)
    temp_health = Column(Integer)
    current_health = Column(Integer)
    health_roll = Column(Text)
    armor_class = Column(Integer)
    initiative_bonus = Column(Integer)
    initiative = Column(Integer)
    speed = Column(Integer)
    strength = Column(Integer)
    dexterity = Column(Integer)
    constitution = Column(Integer)
    intelligence = Column(Integer)
    wisdom = Column(Integer)
    charisma = Column(Integer)
    strength_save = Column(Integer)
    dexterity_save = Column(Integer)
    constitution_save = Column(Integer)
    intelligence_save = Column(Integer)
    wisdom_save = Column(Integer)
    charisma_save = Column(Integer)
    status = Column(Integer)
    damage_vulnerabilities = Column(Text)
    damage_resistances = Column(Text)
    damage_immunities = Column(Text)
    condition_immunities = Column(Text)
    senses = Column(Text)
    languages = Column(Text)
    challenge_rating = Column(Text)
    legendary_actions_count = Column(Integer)
    actions = relationship('Actions')
    legendary_actions = relationship('LegendaryActions')
    special_abilities = relationship('SpecialAbilities')
    encounter_id = Column(Integer, ForeignKey('encounter.id'))
    encounter = relationship('Encounter', back_populates='characters')

    __mapper_args__ = {'polymorphic_identity': 'character', 'polymorphic_on': type}

    def to_tuple(self):
        return 0

    def alive(self):
        return self.current_health > 0

    def damage(self, dealt_damage):
        self.current_health -= dealt_damage
        self.temp_health -= dealt_damage
        if self.temp_health < 0:
            self.temp_health = 0
        if self.current_health <= 0:
            self.status = Status.DEAD
            self.current_health = 0

    def add_temp_health(self, health):
        self.current_health += health
        self.temp_health += health

    def heal(self, healed_damage):
        if self.status != Status.DEAD:
            self.current_health += healed_damage
            if self.current_health > self.max_health + self.temp_health:
                self.current_health = self.max_health + self.temp_health
            if self.status != Status.ALIVE:
                self.status = Status.ALIVE

    def adjust_max_health(self, health):
        self.max_health += health
        self.current_health += health

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
        return 0
