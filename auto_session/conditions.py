class Or(object):
    def __init__(self, *conditions):
        self.conditions = conditions

    def __call__(self, *args, **kwargs):
        for c in self.conditions:
            if c(*args, **kwargs):
                return True

        return False


class Received(object):
    def __init__(self, frame_type, min_count=None):
        self.frame_type = frame_type
        self.min_count = min_count

    def __call__(self, *args, **kwargs):
        return True


class Iterations(object):
    def __init__(self, count):
        self.count = count

    def __call__(self, *args, **kwargs):
        return True

