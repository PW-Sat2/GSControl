import sys, time, pprint
sys.path.append('../..')

import tmtc
from tm import TM, Check
from tmtc import Tmtc
from tc.comm import EnterIdleState, SendBeacon


tmtc = Tmtc()
checker = Check(tmtc)



time.sleep(15)

checker.check(TM.COMM.TX.IdleState, False, 0)


tmtc.send(EnterIdleState(100))
checker.check(TM.COMM.TX.IdleState, True, 0)
checker.check(TM.COMM.TX.IdleState, False, 100)

tmtc.send(EnterIdleState(255))
checker.check(TM.COMM.TX.IdleState, True, 0)
tmtc.send(EnterIdleState(0))
checker.check(TM.COMM.TX.IdleState, False, 0)