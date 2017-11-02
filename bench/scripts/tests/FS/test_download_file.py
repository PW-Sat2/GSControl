import sys, time, pprint
sys.path.append('../../..')

import tmtc
from tm import TM, Check
from tmtc import Tmtc
from tc.fs import DownloadFile, GetFileInfo
from tools.remote_files import RemoteFileTools

tmtc = Tmtc()
checker = Check(tmtc)

time.sleep(1)

# Request info about particular file
chosen_file = tmtc.send(GetFileInfo('/', 'telemetry.current'))
pprint.pprint(chosen_file)

# Download file
chunks = tmtc.send(DownloadFile(chosen_file["File"], chosen_file["Chunks"]))

# Save file
RemoteFileTools.save_chunks('downloaded.raw', chunks)
