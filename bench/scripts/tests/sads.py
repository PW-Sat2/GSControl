from bench_init import *

import time


@make_test
def test_sads_run_and_abort():
    # Be sure that no experiment is currently running
    tm.assert_equal(tm.Experiments.CurrentExperimentCode, 'None')

    # Request sads experiment and check whether is running
    send(tc.experiments.PerformSADSExperiment())
    tm.assert_equal(tm.Experiments.CurrentExperimentCode, 'SADS', timeout=180)

    # Abort sads experiment and check whether operation is successful
    send(tc.experiments.AbortExperiment())
    tm.assert_equal(tm.Experiments.CurrentExperimentCode, 'None', timeout=15)


@make_test
def test_sads_full_experiment():
    PrintLog('Remove sads files if present')
    scripts.fs.remove_file('sads.photo_wing')
    scripts.fs.remove_file('sads.exp')

    PrintLog('Be sure that no experiment is currently running')
    tm.assert_equal(tm.Experiments.CurrentExperimentCode, 'None')

    PrintLog('Request sads experiment and check whether is running')
    send(tc.experiments.PerformSADSExperiment())
    tm.assert_equal(tm.Experiments.CurrentExperimentCode, 'SADS', timeout=300)

    PrintLog('Wait till the experiment is finished')
    tm.assert_equal(tm.Experiments.CurrentExperimentCode, 'None', timeout=1000)

    PrintLog('Wait till all files are saved')
    time.sleep(180)

    tm.assert_equal(tm.Experiments.CurrentExperimentCode, 'None')

    PrintLog('Download file sads.exp')
    scripts.fs.download_file('sads.exp')

    PrintLog('Get sads.photo_wing')
    scripts.fs.download_photo('sads.photo_wing')
