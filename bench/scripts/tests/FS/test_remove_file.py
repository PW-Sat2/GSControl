import pprint

from bench_init import *

# Request info about particular file
chosen_file = send(tc.fs.GetFileInfo('/', 'telemetry.current'))
pprint.pprint(chosen_file)

# Remove file
send(tc.fs.RemoveFile('telemetry.current'))

# Request info about particular file - should be None
chosen_file = send(tc.fs.GetFileInfo('/', 'telemetry.current'))
pprint.pprint(chosen_file)

# Remove file if exists
resp = send(tc.fs.RemoveFileIfExists('/', 'aabbcc'))
print(resp)

# Remve non-existing file
send(tc.fs.RemoveFile('aabbcc'))
