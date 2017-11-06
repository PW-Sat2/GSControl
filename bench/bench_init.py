import os

import tmtc.tmtc
import tmtc.tc
import tmtc.tm.tm


class Bench(tmtc.tmtc.Tmtc, tmtc.tm.tm.TM):
    def __init__(self):
        tmtc.tmtc.Tmtc.__init__(self)
        tmtc.tm.tm.TM.__init__(self, self)

bench = Bench()

send = bench.send
get = bench.get

tm = bench
tc = tmtc.tc


def make_test(method):
    def make_test_decorator(*args, **kw):
        from tools.tools import MainLog
        from config import config

        test_name = method.__name__

        MainLog("Starting test {}".format(test_name))

        asrun = os.path.join(config['output_path'], test_name)

        suffix = 0
        while os.path.isfile(asrun + '_' + str(suffix) + ".log"):
            suffix += 1
        config['asrun_name'] = test_name + '_' + str(suffix) + ".log"

        result = method(*args, **kw)

        config['asrun_name'] = "repl.log"
        MainLog("Finishing test {}".format(test_name))

        return result
    return make_test_decorator

import scripts

from tools.tools import PrintLog, MainLog, SimpleLogger
from tools.checks import *