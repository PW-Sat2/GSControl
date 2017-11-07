from bench_init import *

import time
from tools.tools import RandomString


@make_test
def test_radfet_calibration():
    # Check if OBC Terminal is available
    print(obc.ping())

    # Be sure that no experiment is currently running
    tm.assert_equal(tm.Experiments.CurrentExperimentCode, 'None')

    print(obc.enable_lcl(5))
    print(obc.payload_radfet_on())
    time.sleep(10)

    for i in range(10):
        print(obc.payload_radfet_read())

    print(obc.payload_radfet_off())
    print(obc.disable_lcl(5))
