from bench_init import *

import time
from tools.tools import RandomString, CSVLogger


@make_test
def test_radfet_calibration(duration):
    logger = CSVLogger('radfet_thermal')

    # Check if OBC Terminal is available
    print(obc.ping())

    # Be sure that no experiment is currently running
    tm.assert_equal(tm.Experiments.CurrentExperimentCode, 'None')

    print(obc.enable_lcl(5))
    time.sleep(5)

    print(obc.payload_radfet_on())

    time.sleep(10)

    for i in range(duration):
        radfet_data = obc.payload_radfet_read()
        temps_data = obc.payload_temps()
        all_data = [radfet_data, temps_data]
        print(all_data)
        logger.write_row(all_data)

    print(obc.payload_radfet_off())
    print(obc.disable_lcl(5))
