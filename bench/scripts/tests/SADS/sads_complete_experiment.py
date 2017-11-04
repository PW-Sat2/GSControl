from bench_init import *

import time, pprint

from tools.remote_files import RemoteFileTools
from tools.tools import PrintLog as PrintLog

PrintLog('Remove SADS files if present')
res = send(tc.fs.RemoveFileIfExists('/', 'sads.photo_wing'))
print(res)
res = send(tc.fs.RemoveFileIfExists('/', 'sads.exp'))
print(res)

PrintLog('Be sure that no experiment is currently running')
check(tm.Experiments.CurrentExperimentCode, 'None', 0)

PrintLog('Request SADS experiment and check whether is running')
send(tc.experiments.PerformSADSExperiment())
check(tm.Experiments.CurrentExperimentCode, 'SADS', 300)

PrintLog('Wait till the experiment is finished')
check(tm.Experiments.CurrentExperimentCode, 'None', 1000)

PrintLog('Wait till all files are saved')
time.sleep(180)

PrintLog('Get sads.exp')
PrintLog('Request info about particular file')
chosen_file = send(tc.fs.GetFileInfo('/', 'sads.exp'))
pprint.pprint(chosen_file)

if chosen_file is not None:
    PrintLog('Download file sads.exp')
    chunks = send(tc.fs.DownloadFile(chosen_file["File"], chosen_file["Chunks"]))

    PrintLog('Save file sads.exp')
    RemoteFileTools.save_chunks('sads.exp.raw', chunks)
else:
    PrintLog('File sads.exp does not exist')

PrintLog('Get sads.photo_wing')
PrintLog('Request info about particular file')
chosen_file = send(tc.fs.GetFileInfo('/', 'sads.photo_wing'))
pprint.pprint(chosen_file)

if chosen_file is not None:
    PrintLog('Download file sads.photo_wing')
    chunks = send(tc.fs.DownloadFile(chosen_file["File"], chosen_file["Chunks"]))

    PrintLog('Save file sads.photo_wing')
    RemoteFileTools.save_chunks('sads.photo_wing.raw', chunks)
    PrintLog('Save photo sads.photo_wing')
    RemoteFileTools.save_photo('sads.photo_wing.jpg', chunks)
else:
    PrintLog('File sads.photo_wing does not exist')
