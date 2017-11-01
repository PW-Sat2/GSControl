import sys, time, pprint
sys.path.append('../..')

import tmtc
from tm import TM, Check
from tmtc import Tmtc
from tc.experiments import AbortExperiment, PerformSADSExperiment
from tc.comm import SendBeacon

tmtc = Tmtc()
checker = Check(tmtc)

time.sleep(1)

tmtc.send(SendBeacon())
time.sleep(5)
checker.check(TM.Experiments.CurrentExperimentCode, 'None', 0)


tmtc.send(PerformSADSExperiment())
tmtc.send(SendBeacon())
time.sleep(5)
checker.check(TM.Experiments.CurrentExperimentCode, 'SADS', 300)

tmtc.send(AbortExperiment())
tmtc.send(SendBeacon())
time.sleep(5)
checker.check(TM.Experiments.CurrentExperimentCode, 'None', 200)
