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
get = bench.get

tm = tmtc.tm.TM
tc = tmtc.tc
