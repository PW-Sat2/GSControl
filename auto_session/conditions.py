from datetime import datetime, timedelta


class Or(object):
    def __init__(self, *conditions):
        self.conditions = conditions

    def __call__(self, *args, **kwargs):
        for c in self.conditions:
            if c(*args, **kwargs):
                return True

        return False


class Received(object):
    def __init__(self, frame_type, min_count=1):
        self.frame_type = frame_type
        self.min_count = min_count

    def __call__(self, received_frames):
        x = filter(lambda f: isinstance(f, self.frame_type), received_frames)
        return len(x) >= self.min_count


class Iterations(object):
    def __init__(self, count):
        self.count = count

    def __call__(self, *args, **kwargs):
        return True


class PointOfTime(object):
    def __init__(self, time_to_stop):
        self.end = time_to_stop

    def __call__(self, *args, **kwargs):
        return datetime.now() >= self.end


class Eternity(object):
    def __call__(self, *args, **kwargs):
        return False
