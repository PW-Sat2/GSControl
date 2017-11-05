import time
import os
import datetime
import pprint

from config import config

class SimpleLogger:
    def __init__(self, path):
        self.path = os.path.join(config['output_path'], path)
        self.f = open(self.path, 'a')
        self.f.close()

    @staticmethod
    def format(data):
        return '[' + time.strftime('%H:%M:%S') + '] ' + data.strip()

    def log(self, data):
        self.f = open(self.path, 'a')
        self.f.writelines(self.format(data) + '\n')
        self.f.close()


def PrintLog(*text, **kwargs):
    line = ' '.join([str(i) for i in text])
    print SimpleLogger.format(line)
    name = config['asrun_name']
    if kwargs.pop('main', False):
        name = "main.log"
    SimpleLogger(name).log(line)


def MainLog(*text):
    PrintLog(*text, main=True)