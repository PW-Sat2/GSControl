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
