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
        from tools.log import MainLog
        from config import config

        test_name = method.__name__

        folder_name = os.path.join(config['output_path'], test_name + "_")
        suffix = 0
        while os.path.isdir(folder_name + str(suffix)):
            suffix += 1
        folder_name += str(suffix)
        os.makedirs(folder_name)
        test_name += "_" + str(suffix)
        config['test_name'] = test_name

        MainLog("Starting test {}".format(test_name))
        result = method(*args, **kw)
        MainLog("Finishing test {}".format(test_name))

        config['test_name'] = ""

        return result
    return make_test_decorator

import scripts

from tools.log import PrintLog, MainLog, SimpleLogger
from tools.checks import *