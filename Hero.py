from Character import Character


class Hero(Character):
    def __init__(self, name, health, ac, initiative, speed, player):
        super().__init__(name, health, ac, initiative, speed)
        self.player = player
