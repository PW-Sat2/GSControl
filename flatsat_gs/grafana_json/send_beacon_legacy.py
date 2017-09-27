import imp
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../build/integration_tests'))
import response_frames
from binascii import hexlify
from experiment_file import ExperimentFileParser
from utils import ensure_string

from radio.radio_receiver import *
from radio.radio_sender import *
from tools.remote_files import *
from tools.parse_beacon import *

from telecommand import *
from response_frames import operation
from devices import comm
from tools.tools import SimpleLogger
import datetime
import pprint
import time
from ftplib import FTP
from datetime import datetime


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--target_gr', required=True,
                        help="GNURadio host", default='localhost')                 
    parser.add_argument('-p', '--port_gr', required=True,
                        help="GNURadio port", default=52002, type=int)

    args = parser.parse_args()

    receiver = Receiver(args.target_gr, args.port_gr)
    receiver.connect()

    while True:
        try:
            recv = receiver.receive_frame()
            print(recv)

            if isinstance(recv, comm.BeaconFrame):
                ftp = FTP('ftp.cluster021.hosting.ovh.net')
                ftp.login('gumielanjx', 'PWSat2GS')
                ftp.cwd('www/pwsat2')
                fr = open('telemetry.json', 'w')
                f = open('index.html', 'w')
                flog = open('beacon.log', 'a')
                rawb = ParseBeacon.parse(recv)
                rawb['00: Last update'] = {'date' : datetime.date(datetime.now()), 'time' : datetime.time(datetime.now())}
                beacon = ParseBeacon.convert(rawb)
                
                pprint.pprint(beacon, flog)

                f.writelines("<html><head><meta http-equiv=\"refresh\" content=\"10\"></head><body><pre>")
                pprint.pprint(beacon, f)
                f.writelines("</pre></body></html>")
                j = ParseBeacon.convert_json(rawb)
                fr.write(j)
                pprint.pprint(j)

                f.close()
                fr.close()
                flog.close()
                fr = open('telemetry.json', 'r')
                f = open('index.html', 'r')
                ftp.storlines("STOR index.html", f)
                ftp.storlines("STOR telemetry.json", fr)
                f.close()
                fr.close()
                ftp.close()
        except:
            pass
    




