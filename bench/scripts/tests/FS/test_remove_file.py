import sys, time, pprint
sys.path.append('../../..')

import tmtc
from tm import TM, Check
from tmtc import Tmtc
from tc.fs import GetFileInfo, RemoveFile

tmtc = Tmtc()
checker = Check(tmtc)

time.sleep(1)

# Request info about particular file
chosen_file = tmtc.send(GetFileInfo('/', 'telemetry.current'))
pprint.pprint(chosen_file)

# Remove file
tmtc.send(RemoveFile('telemetry.current'))

# Request info about particular file - should be None
chosen_file = tmtc.send(GetFileInfo('/', 'telemetry.current'))
pprint.pprint(chosen_file)

# Remve non-existing file
tmtc.send(RemoveFile('aabbcc'))
