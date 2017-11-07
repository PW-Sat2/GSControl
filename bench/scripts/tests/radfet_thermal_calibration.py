from bench_init import *

import time, datetime
from tools.tools import RandomString, CSVLogger
import progressbar


@make_test
def test_radfet_calibration(duration):
    bar = progressbar.ProgressBar(redirect_stdout=True, max_value=duration)
    logger = CSVLogger('radfet_thermal')

    # Check if OBC Terminal is available
    print(obc.ping())

    # Be sure that no experiment is currently running
    tm.assert_equal(tm.Experiments.CurrentExperimentCode, 'None')

    print(obc.enable_lcl(5))
    time.sleep(5)

    print(obc.payload_radfet_on())

    time.sleep(10)

    start_time = time.time()
    stop_time = start_time + duration*60

    print "Stop time: ", datetime.datetime.fromtimestamp(stop_time)

    while time.time() < stop_time:
        radfet_data = obc.payload_radfet_read()
        temps_data = obc.payload_temps()
        all_data = [radfet_data, temps_data]
        print(all_data)
        logger.write_row(all_data)

        try:
            bar.update(round((time.time()-start_time)/60, 2))
        except ValueError:
            pass

    print(obc.payload_radfet_off())
    print(obc.disable_lcl(5))
