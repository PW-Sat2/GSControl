import time
import os
import sys

config = dict(
    COMM_SECURITY_CODE=0x46707057,
    GS_HOST="10.100.0.200",
    SOURCE_CALLSIGN="SP3SAT",
    DESTINATION_CALLSIGN="PWSAT2",
    LOGGERS=['swo', 'saleae'],
    session_name="",
    output_path="",
    asrun_name=""
)

session_name = time.strftime("%Y-%m-%d_%H:%M:%S_") + sys.argv[1]
config['session_name'] = session_name
config['output_path'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs', config['session_name']))

os.makedirs(config['output_path'])
