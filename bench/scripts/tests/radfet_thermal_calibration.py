from bench_init import *

import time, datetime
from tools.log import CSVLogger
import progressbar


@make_test
def test_radfet_calibration(stabilization_time, duration):
    bar = progressbar.ProgressBar(max_value=duration)
    logger = CSVLogger('radfet_thermal.csv', in_test=True)

    # Check if OBC Terminal is available
    print(obc.ping())

    # Be sure that no experiment is currently running
    tm.assert_equal(tm.OBC.Experiments.Code, 'None')

    print(obc.enable_lcl(5))

    # stabilization time
    time.sleep(stabilization_time)

    print(obc.payload_radfet_on())

    time.sleep(10)

    start_time = time.time()
    stop_time = start_time + duration*60

    print "Stop time: ", datetime.datetime.fromtimestamp(stop_time)

    while time.time() < stop_time:
        radfet_data = obc.payload_radfet_read()
        temps_data = obc.payload_temps()
        all_data = dict(radfet_data, **temps_data)
        print(all_data)
        logger.log(all_data)

        try:
            bar.update(round((time.time()-start_time)/60, 2))
        except ValueError:
            pass

    print(obc.payload_radfet_off())
    print(obc.disable_lcl(5))
