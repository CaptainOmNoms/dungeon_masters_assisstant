class Character(object):
    """Any PC or NPC in an encounter"""

    def __init__(self, name, health, ac, initiative, speed):
        self.name = name
        self.health = health
        self.ac = ac
        self.initiative = initiative
        self.speed = speed
        self.alive = True

    def damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def heal(self, heal):
        self.health += heal

    def print(self):
        print("{0}, Health: {1} Initiative: {2} AC: {3} Speed: {4}".format(self.name, self.health, self.initiative, self.ac, self.speed))
        # TODO add attacks print out
