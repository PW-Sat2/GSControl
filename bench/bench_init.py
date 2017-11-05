import atexit
import sys
import os

from config import config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'integration_tests')))

import tmtc.tmtc
import tmtc.tc
import tmtc.tm.tm
from tools.loggers import *

from tools.tools import MainLog
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


class Bench(tmtc.tmtc.Tmtc, tmtc.tm.tm.Check):
    def __init__(self):
        tmtc.tmtc.Tmtc.__init__(self)
        tmtc.tm.tm.Check.__init__(self, self)

bench = Bench()

send = bench.send
check = bench.check

tm = tmtc.tm.TM
tc = tmtc.tc
