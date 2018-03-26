from sqlalchemy import Column, Integer

from monster_tracker.models import Status
from monster_tracker.models.characters import Character


class Monster(Character):
    experience = Column(Integer, default=0)

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
