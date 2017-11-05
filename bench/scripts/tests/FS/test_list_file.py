from bench_init import *
from tools.tools import PrintLog


def run():
    # Request file list
    file_list = send(tc.fs.ListFiles('/'))
    PrintLog("Files present: ", file_list)

    # Request info about particular file
    chosen_file = send(tc.fs.GetFileInfo('/', 'telemetry.current'))
    PrintLog(chosen_file)

    # Request info about non-existing file
    non_existing = send(tc.fs.GetFileInfo('/', 'aaabbbccc'))
    PrintLog(non_existing)
