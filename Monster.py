from Character import Character


class Monster(Character):
    """Any NPC"""
    def __init__(self, name, health, ac, initiative, speed, xp):
        super().__init__(name, health, ac, initiative, speed)
        self.xp = xp


#TODO create lookup function
