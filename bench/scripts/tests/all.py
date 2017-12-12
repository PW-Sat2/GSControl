import sys

from tools.tools import handle_exception

from bench_init import *


def try_test(test):
    try:
        test()
    except KeyboardInterrupt:
        raise
    except Exception:
        etype, value, tb = sys.exc_info()
        handle_exception(etype, value, tb)


def test_all():
    try_test(scripts.tests.comm.test_comm_idle_state)
    try_test(scripts.tests.fs.test_fs_download_file)
    try_test(scripts.tests.fs.test_fs_list_file)
    try_test(scripts.tests.fs.test_fs_remove_file)
    try_test(scripts.tests.sads.test_sads_run_and_abort)
    try_test(scripts.tests.sads.test_sads_full_experiment)
    try_test(scripts.tests.camera.test_camera_telecommand)