class Dice(object):

    def __init__(self, sides, number):
        self.sides = sides
        self.number = number

    def check_roll(self, roll):
        if roll > self.sides * self.number:
            return -1
        else:
            return roll
