import sys, time, pprint
sys.path.append('../../..')

import tmtc
from tm import TM, Check
from tmtc import Tmtc
from tc.fs import ListFiles, GetFileInfo

tmtc = Tmtc()
checker = Check(tmtc)

time.sleep(1)


# Request file list
file_list = tmtc.send(ListFiles('/'))
pprint.pprint(file_list)

# Request info about particular file
chosen_file = tmtc.send(GetFileInfo('/', 'telemetry.current'))
pprint.pprint(chosen_file)

# Request info about non-existing file
non_existing = tmtc.send(GetFileInfo('/', 'aaabbbccc'))
pprint.pprint(non_existing)
