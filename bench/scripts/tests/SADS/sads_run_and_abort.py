import sys, time, pprint
sys.path.append('../../..')

import tmtc
from tm import TM, Check
from tmtc import Tmtc
from tc.experiments import AbortExperiment, PerformSADSExperiment
from tc.comm import SendBeacon

tmtc = Tmtc()
checker = Check(tmtc)

time.sleep(1)

# Be sure that no experiment is currently running
checker.check(TM.Experiments.CurrentExperimentCode, 'None', 0)

# Request SADS experiment and check whether is running
tmtc.send(PerformSADSExperiment())
checker.check(TM.Experiments.CurrentExperimentCode, 'SADS', 180)

# Abort SADS experiment and check whether operation is successful
tmtc.send(AbortExperiment())
checker.check(TM.Experiments.CurrentExperimentCode, 'None', 180)
