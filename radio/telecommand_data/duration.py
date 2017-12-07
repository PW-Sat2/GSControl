class Duration:
    def __init__(self, *args):
        if len(args) == 1:
            self.minimum = args[0]
            self.maximum = args[0]
        else:
            self.minimum = args[0]
            self.maximum = args[1]

    def min(self):
        return self.minimum

    def max(self):
        return self.maximum

    def __add__(self, other):
        return Duration(self.min() + other.min(), self.max() + other.max())

    def __str__(self):
        return '{}-{}'.format(self.minimum, self.maximum) if self.minimum != self.maximum else str(self.minimum)
