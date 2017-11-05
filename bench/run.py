import sys
import os
import traceback
from argparse import ArgumentParser

from bench_init import *
from tools.tools import MainLog, PrintLog

parser = ArgumentParser()
parser.add_argument("name", nargs=1, help='Name of test session')
parser.add_argument("scripts", nargs="*", help='Scripts to run, as path to file')
args = parser.parse_args()

MainLog("Scripts to run: ", args.scripts)


def foo(exctype, value, tb):
    PrintLog('Uncaught exception!')
    PrintLog('{0}: {1}'.format(exctype, value))
    PrintLog(''.join(traceback.format_tb(tb)))
    MainLog("Test {} failed!".format(config['asrun_name']))

sys.excepthook = foo

for i in sys.argv[2:]:
    MainLog("Starting test {}".format(i))

    module_dir, module_file = os.path.split(i)
    module_name, module_ext = os.path.splitext(module_file)

    from config import config

    asrun = os.path.join(config['output_path'], module_name)

    suffix = 0
    while os.path.isfile(asrun + '_' + str(suffix)):
        suffix += 1
    config['asrun_name'] = module_name + '_' + str(suffix)

    path = os.path.join(os.getcwd(), module_dir)
    sys.path.append(path)
    module_obj = __import__(module_name)

    module_obj.run()

    sys.path.pop()

    MainLog("Finishing test {}".format(i))


