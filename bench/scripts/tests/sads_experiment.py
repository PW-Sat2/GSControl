import sys, time, pprint
sys.path.append('../..')

import tmtc
from tm import TM, Check
from tmtc import Tmtc
from tc.experiments import AbortExperiment, PerformSADSExperiment


tmtc = Tmtc()
checker = Check(tmtc)

time.sleep(15)

checker.check(TM.Experiments.CurrentExperimentCode, False, 0)


tmtc.send(PerformSADSExperiment())
checker.check(TM.Experiments.CurrentExperimentCode, 6, 200)

tmtc.send(AbortExperiment())
checker.check(TM.Experiments.CurrentExperimentCode, False, 200)
