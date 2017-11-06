import sys
import os
import traceback
import time
import atexit
from argparse import ArgumentParser

from IPython.terminal.embed import InteractiveShellEmbed
from IPython.terminal.prompts import Prompts
from pygments.token import Token

from config import config
from tools.tools import MainLog, handle_exception
from tools.loggers import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'integration_tests')))

parser = ArgumentParser()
parser.add_argument("session_name", nargs=1, help='Name of test session')
cmd_line_args = parser.parse_args()


config['session_name'] = time.strftime("%Y-%m-%d_%H:%M:%S_") + cmd_line_args.session_name[0]
config['output_path'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs', config['session_name']))
os.makedirs(config['output_path'])


MainLog("Starting session:", config['session_name'])


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


def custom_exc(shell, etype, evalue, tb, tb_offset=None):
    handle_exception(etype, evalue, tb)
    shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)


class MyPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [(Token.Prompt, 'Bench'),
                (Token.Prompt, '> ')]


shell = InteractiveShellEmbed(user_ns={},
                              banner2='Bench Terminal')
shell.prompts = MyPrompt(shell)
shell.run_code('import scripts')
shell.run_code('from bench_init import *')
shell.set_custom_exc((Exception,), custom_exc)


# sys.excepthook = exception_hook
shell()
