import sys
import os
import traceback
import time
import atexit
from argparse import ArgumentParser

from config import config
from tools.tools import MainLog, PrintLog
from tools.loggers import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'integration_tests')))

parser = ArgumentParser()
parser.add_argument("session_name", nargs=1, help='Name of test session')
parser.add_argument("scripts", nargs="*", help='Scripts to run, as path to file', default=[])
cmd_line_args = parser.parse_args()


config['session_name'] = time.strftime("%Y-%m-%d_%H:%M:%S_") + cmd_line_args.session_name[0]
config['output_path'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs', config['session_name']))
os.makedirs(config['output_path'])


MainLog("Starting session:", config['session_name'])
MainLog("Scripts to run: ", cmd_line_args.scripts)


loggers = []
loggers_map = {'swo': JlinkSWOLogger, 'uart': UARTLogger, 'saleae': SaleaeLogger}

MainLog("Starting loggers {}...".format(config['LOGGERS']))
for i in config['LOGGERS']:
    name = i.split(' ')[0]
    args = i.split(' ')[1:]
    logger_type = loggers_map[name]
    loggers.append(logger_type(*args))
    print "Loggers: ", loggers

for logger in loggers:
    logger.start()
MainLog("Loggers {} started.".format(loggers))


def cleanup(enabled_loggers):
    from tools.tools import MainLog
    MainLog("Stopping loggers {}".format(enabled_loggers))
    for log in enabled_loggers:
        log.stop()
    MainLog("Loggers stopped.")
    from config import config
    MainLog("Closing session:", config['session_name'])

atexit.register(cleanup, loggers)


def exception_hook(exctype, value, tb):
    PrintLog('Uncaught exception!')
    PrintLog('{0}: {1}'.format(exctype, value))
    PrintLog(''.join(traceback.format_tb(tb)))
    MainLog("Test {} failed!".format(config['asrun_name']))

sys.excepthook = exception_hook


def run_test(name):
    try:
        MainLog("Starting test {}".format(name))

        module_dir, module_file = os.path.split(name)
        module_name, module_ext = os.path.splitext(module_file)

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

    finally:
        config['asrun_name'] = "repl.log"
        MainLog("Finishing test {}".format(name))

for i in cmd_line_args.scripts:
    run_test(i)

if len(cmd_line_args.scripts) == 0:
    from IPython.terminal.embed import InteractiveShellEmbed
    from IPython.terminal.prompts import Prompts
    from pygments.token import Token

    class MyPrompt(Prompts):
        def in_prompt_tokens(self, cli=None):
            return [(Token.Prompt, 'Bench'),
                    (Token.Prompt, '> ')]


    config['asrun_name'] = "repl.log"
    shell = InteractiveShellEmbed(user_ns={'run_test': run_test},
                                  banner2='TMTC Terminal')
    shell.prompts = MyPrompt(shell)
    shell.run_code('from bench_init import *')
    shell()