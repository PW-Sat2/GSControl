import sys, time, pprint
sys.path.append('../../..')

import tmtc
from tm import TM, Check
from tmtc import Tmtc
from tc.fs import ListFiles

tmtc = Tmtc()
checker = Check(tmtc)

time.sleep(1)


# Request file list
file_list = tmtc.send(ListFiles())

pprint.pprint(file_list)
