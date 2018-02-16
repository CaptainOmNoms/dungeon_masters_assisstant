class Character():
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

    def heal(self, potion):
        self.health += potion




