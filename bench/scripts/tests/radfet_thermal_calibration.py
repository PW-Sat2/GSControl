from bench_init import *

import time, datetime
from tools.log import CSVLogger
import progressbar


@make_test
def test_radfet_calibration(stabilization_time, duration, filename):
    bar = progressbar.ProgressBar(max_value=duration.total_seconds()/60)
    logger = CSVLogger(filename, in_test=True)

    # Check if OBC Terminal is available
    PrintLog("OBC ping:", obc.ping())

    # Be sure that no experiment is currently running
    tm.assert_equal(tm.OBC.Experiments.Code, 'None')

    PrintLog("OBC enable PLD LCL:", obc.enable_lcl(5))
    time.sleep(5)

    PrintLog("Radfet ON:", obc.payload_radfet_on())
    # stabilization time
    time.sleep(stabilization_time.total_seconds())

    start_time = time.time()
    stop_time = start_time + duration.total_seconds()

    PrintLog("Stop time:" + str(datetime.datetime.fromtimestamp(stop_time)))

    while time.time() < stop_time:
        radfet_data = obc.payload_radfet_read()
        temps_data = obc.payload_temps()

        PrintLog("Data point at {}:".format(time.time()), radfet_data, temps_data)
        logger.log({"timestamp": time.time()}, radfet_data, temps_data)

        try:
            bar.update(round((time.time()-start_time)/60, 2))
        except ValueError:
            pass

    PrintLog("Radfet off:", obc.payload_radfet_off())
    PrintLog("Disable PLD LCL:", obc.disable_lcl(5))
