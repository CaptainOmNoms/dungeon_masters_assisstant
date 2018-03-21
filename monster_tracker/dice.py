import ui


class Dice(object):
    """
    Helps validate dice rolls
    """

    def __init__(self, number, sides):
        self.number = number
        self.sides = sides

    def check_roll(self, roll):
        if roll > self.sides * self.number:
            ui.info(ui.red, 'Are you sure you\'re using a d20?')
            return 0
        return roll
