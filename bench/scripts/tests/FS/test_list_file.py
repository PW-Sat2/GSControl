import pprint

from bench_init import *


# Request file list
file_list = send(tc.fs.ListFiles('/'))
pprint.pprint(file_list)

# Request info about particular file
chosen_file = send(tc.fs.GetFileInfo('/', 'telemetry.current'))
pprint.pprint(chosen_file)

# Request info about non-existing file
non_existing = send(tc.fs.GetFileInfo('/', 'aaabbbccc'))
pprint.pprint(non_existing)
