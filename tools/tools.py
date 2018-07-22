import time
import pprint

class SimpleLogger:
    def __init__(self, path):
        self.path = path
        self.f = open(self.path, 'a')
        self.f.close()

    def log(self, data):
        self.f = open(self.path, 'a')
        t = '[' + time.strftime('%x %X') + '] '
        self.f.writelines(t + pprint.pformat(data) + '\n')
        self.f.close()