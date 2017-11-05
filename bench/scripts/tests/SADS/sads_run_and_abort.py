from bench_init import *


def run():
    # Be sure that no experiment is currently running
    check(tm.Experiments.CurrentExperimentCode, 'None', 0)

    # Request SADS experiment and check whether is running
    send(tc.experiments.PerformSADSExperiment())
    check(tm.Experiments.CurrentExperimentCode, 'SADS', 180)

    # Abort SADS experiment and check whether operation is successful
    send(tc.experiments.AbortExperiment())
    check(tm.Experiments.CurrentExperimentCode, 'None', 180)
