import traceback

from log import PrintLog, MainLog
import string
import random


def handle_exception(etype, evalue, tb):
    from config import config
    PrintLog('Uncaught exception!')
    PrintLog('{0}: {1}'.format(etype, evalue))
    PrintLog(''.join(traceback.format_exception(etype, evalue, tb)))
    MainLog("Test {} failed!".format(config['test_name']))
    config['test_name'] = ""
    config['files_path'] = config['output_path']


def RandomString(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


class CSVLogger:
    def __init__(self, base_name):
        self.output = open(base_name + "_" + str(time.time()), 'a')
        self.header_exists = False

    def write_header(self, dicts):
        header = "timestamp;"
        for d in dicts:
            for key in d:
                header += str(key) + ";"
        header += "\n"
        self.output.write(header)

    def write_row(self, dicts):
        if self.header_exists is False:
            self.write_header(dicts)
            self.header_exists = True

        row = str(time.time()) + ";"
        for d in dicts:
            for key in d.itervalues():
                row += str(key) + ";"
        row += "\n"
        self.output.write(row)     
