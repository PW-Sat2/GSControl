import sys, time, pprint
sys.path.append('../../..')

import tmtc
from tm import TM, Check
from tmtc import Tmtc
from tc.experiments import AbortExperiment, PerformSADSExperiment
from tc.comm import SendBeacon
from tc.fs import GetFileInfo, RemoveFile, RemoveFileIfExists, DownloadFile
from tools.remote_files import RemoteFileTools
from tools.tools import PrintLog as PrintLog

tmtc = Tmtc()
checker = Check(tmtc)

PrintLog('Remove SADS files if present')
res = tmtc.send(RemoveFileIfExists('/', 'sads.photo_wing'))
print(res)
res = tmtc.send(RemoveFileIfExists('/', 'sads.exp'))
print(res)

PrintLog('Be sure that no experiment is currently running')
checker.check(TM.Experiments.CurrentExperimentCode, 'None', 0)

PrintLog('Request SADS experiment and check whether is running')
tmtc.send(PerformSADSExperiment())
checker.check(TM.Experiments.CurrentExperimentCode, 'SADS', 300)

PrintLog('Wait till the experiment is finished')
checker.check(TM.Experiments.CurrentExperimentCode, 'None', 1000)

PrintLog('Wait till all files are saved')
time.sleep(180)

PrintLog('Get sads.exp')
PrintLog('Request info about particular file')
chosen_file = tmtc.send(GetFileInfo('/', 'sads.exp'))
pprint.pprint(chosen_file)

if chosen_file != None:
	PrintLog('Download file sads.exp')
	chunks = tmtc.send(DownloadFile(chosen_file["File"], chosen_file["Chunks"]))

	PrintLog('Save file sads.exp')
	RemoteFileTools.save_chunks('sads.exp.raw', chunks)
else:
	PrintLog('File sads.exp does not exist')

PrintLog('Get sads.photo_wing')
PrintLog('Request info about particular file')
chosen_file = tmtc.send(GetFileInfo('/', 'sads.photo_wing'))
pprint.pprint(chosen_file)

if chosen_file != None:
	PrintLog('Download file sads.photo_wing')
	chunks = tmtc.send(DownloadFile(chosen_file["File"], chosen_file["Chunks"]))

	PrintLog('Save file sads.photo_wing')
	RemoteFileTools.save_chunks('sads.photo_wing.raw', chunks)
	PrintLog('Save photo sads.photo_wing')
	RemoteFileTools.save_photo('sads.photo_wing.jpg', chunks)
else:
	PrintLog('File sads.photo_wing does not exist')
