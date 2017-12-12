from bench_init import *


def remove_file(filename):
    file_info = scripts.fs.get_file_info(filename)

    if file_info is None:
        PrintLog("File {} not present".format(filename))
        return False
    else:
        send(tc.fs.RemoveFile(filename))
        PrintLog("File {} removed!".format(filename))
        return True
