import time
from tools.checks import check_equal
from tools.tools import PrintLog

class TM:
    class COMM:
        class TX:
            IdleState = ['11: Comm', '0665: Transmitter Idle State']

    class Experiments:
        CurrentExperimentCode = ['09: Experiments', '0490: Current experiment code']
        CurrentExperimentStartupResult = ['09: Experiments', '0494: Experiment Startup Result']
        LastExperimentIterationStatus = ['09: Experiments', '0502: Last Experiment Iteration Status']


class Check(object):
    def __init__(self, tmtc):
        self.tmtc = tmtc

    def get(self, name):
        value_actual = self.tmtc.beacon_value(name)
        PrintLog("{}: {}".format(name, value_actual))

    def check(self, name, value, timeout=0):
        timeout += 50  # OBC update 30 second + 10 second TX interval + 5 second RX
        while timeout > 0:
            try:
                value_actual = self.tmtc.beacon_value(name)
                check_equal(name, value_actual, value)
                PrintLog("{}: {} == {}".format(name, value_actual, value))
                return
            except AssertionError:
                # print "Retry"
                time.sleep(1)
                timeout -= 1
        PrintLog("{}: {} != {}".format(name, value_actual, value))
        raise AssertionError()
