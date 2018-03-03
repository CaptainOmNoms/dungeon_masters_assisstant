from .character import Character


class Monster(Character):
    """
    Any NPC
    """

    # TODO Is this docstring accurate?
    def __init__(self, name, health, ac, initiative, speed, xp):
        super().__init__(name, health, ac, initiative, speed)
        self.xp = xp
        # TODO is alive the right word for this. Should there be a marker for being undead?
        self.alive = True


# TODO create lookup function
# TODO database
