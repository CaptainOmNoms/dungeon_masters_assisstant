import ui
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from monster_tracker.models import Base, Status


class Character(Base):  # pylint: disable=too-many-instance-attributes
    __tablename__ = 'character'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    max_health = Column(Integer, default=0)
    temp_health = Column(Integer, default=0)
    current_health = Column(Integer, default=0)
    armor_class = Column(Integer, default=0)
    initiative_bonus = Column(Integer, default=0)
    initiative = Column(Integer, default=0)
    speed = Column(Integer, default=0)
    movement = Column(Integer, default=0)
    status = Column(Integer, default=Status.ALIVE)
    type = Column(Text)
    encounter_id = Column(Integer, ForeignKey('encounter.id'))
    encounter = relationship('Encounter', back_populates='characters')

    __mapper_args__ = {'polymorphic_identity': 'character', 'polymorphic_on': type}

    def to_tuple(self):
        return (
            self.name,
            f'{self.current_health}/{self.max_health}',
            self.armor_class,
            self.initiative,
            f'{self.movement}/{self.speed}',
            Status(self.status).name  # pylint: disable=not-callable
        )

    def alive(self):
        return self.current_health > 0

    def damage(self, dealt_damage):
        raise NotImplementedError('No death for generic character')

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

    def move(self, feet):
        if self.movement > 0:
            if feet <= self.movement:
                self.movement -= feet
            else:
                ui.info(ui.red, 'You can not move more than your speed per turn')
                input()
        else:
            ui.info(ui.red, 'You can not move more than your speed per turn')
            input()

    def act(self):
        pass

    def bonus(self):
        pass

    def turn(self):
        raise NotImplementedError('No turn for generic character')

    def death(self):
        raise NotImplementedError('No death for generic character')

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                print(f'Got extra attr {k}')
        self.status = Status.ALIVE
        self.current_health = self.current_health or self.max_health
        self.movement = self.speed

    def __repr__(self):
        return (
            f'{self.name}, Health: {self.current_health} Initiative: {self.initiative} ' +
            f'AC: {self.armor_class} Speed:{self.speed}'
        )
