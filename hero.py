from .character import Character


class Hero(Character):
    def __init__(self, name, health, ac, initiative, speed, player):
        super().__init__(name, health, ac, initiative, speed)
        if player != '':
            self.player = player
        else:
            self.player = 'DM'

