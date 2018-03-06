class Dice(object):
    """
    Helps validate dice rolls
    """

    def __init__(self, number, sides):
        self.number = number
        self.sides = sides

    def check_roll(self, roll):
        if roll > self.sides * self.number:
            return 0
        else:
            return roll
