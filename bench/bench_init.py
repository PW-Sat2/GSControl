import sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'integration_tests')))

import tmtc.tmtc
import tmtc.tc
import tmtc.tm.tm


class Bench(tmtc.tmtc.Tmtc, tmtc.tm.tm.Check):
    def __init__(self):
        tmtc.tmtc.Tmtc.__init__(self)
        tmtc.tm.tm.Check.__init__(self, self)

bench = Bench()

send = bench.send
check = bench.check

tm = tmtc.tm.TM
tc = tmtc.tc