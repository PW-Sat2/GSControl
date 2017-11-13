from bench_init import *
import time

def wait_for_file(filename, timeout):
    end_time = time.time() + timeout
    while scripts.fs.get_file_info(filename) is None:
    	if end_time < time.time():
    		return False
    	time.sleep(10)

    return True