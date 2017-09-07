import imp
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--file', required=True,
                        help="Log file path")
    parser.add_argument('-e', '--experiment_file', required=True,
                        help="Log file path")
    parser.add_argument('-t', '--target_gr', required=True,
                        help="GNURadio host", default='localhost')                 
    parser.add_argument('-p', '--port_gr', required=True,
                        help="GNURadio port", default=52001, type=int)
    parser.add_argument('-u', '--target_dw', required=True,
                        help="DireWolf host", default='localhost')                 
    parser.add_argument('-v', '--port_dw', required=True,
                        help="DireWolf port", default=8001, type=int)

    args = parser.parse_args()

    sender = Sender(args.target_dw, args.port_dw)
    sender.connect()
    receiver = Receiver(args.target_gr, args.port_gr)
    receiver.connect()
    logger = SimpleLogger(args.file)
    logger.log('Start of the script')

    # 1. receive beacon to see the state of sat before experiment
    print("#1. receive beacon to see the state of sat before experiment")
    while True:
        sender.send(SendBeacon())
        recv = receiver.receive_frame()
        print(recv)

        if isinstance(recv, comm.BeaconFrame):
            break

    beacon = ParseBeacon.parse(recv)
    logger.log('Telemetry before experiment')
    logger.log(beacon)

    # 2. send telecommand to turn on experiment
    print("#2. send telecommand to turn on experiment")
    correlation_id = 2
    delay = 180
    samples_count = 100
    file_name = 'pld_1'

    sender.send(PerformPayloadCommissioningExperiment(correlation_id, file_name))

    # 3. receive, save and parse incomming frames
    count_beacons = 0
    while True:
        print("#3. receive, save and parse incomming frames")
        recv = receiver.receive_frame()
        print(recv)

        if isinstance(recv, comm.BeaconFrame):
            beacon = ParseBeacon.parse(recv)
            pprint.pprint(beacon['08: Experiments'])
            logger.log(beacon)
            count_beacons += 1

            if (count_beacons > 10) and (beacon['08: Experiments']['0518: Current experiment code'] == 0):
                print("Finishing #3.")
                break

        if isinstance(recv, operation.OperationSuccessFrame):
            logger.log(recv.payload())

    # 4. List files
    while True:
        print("#4. list files")
        sender.send(ListFiles(13, '/'))
        recv = receiver.receive_frame()
        print(recv)

        file_list = []
        if isinstance(recv, operation.OperationSuccessFrame):
            file_list = RemoteFileTools.parse_file_list(recv)
            logger.log(file_list)
            print("Finishing #4")
            break

    # 5. Download and save file - primary
    file_to_download = None
    for f in file_list:
        if f['File'] == file_name:
            file_to_download = f
            break
    print("Selecting " + str(file_to_download))
    logger.log(file_to_download)

    downloader = RemoteFile(sender, receiver)
    chunks = downloader.download(file_to_download)
    merged = RemoteFileTools.merge_chunks(chunks)
    print("Download file")
    RemoteFileTools.save_chunks(args.experiment_file, merged)
    
    # 6. Parse file
    try:
        print("#6. Parse file")
        parsed = ExperimentFileParser.parse_partial(ensure_string(merged))
        with open(file_name + "_parsed.txt", 'w') as f:
            for p in parsed[0]:
                pprint.pprint(p, f)

        if len(parsed[1]) > 0:
            print 'Remaining data (first 10 bytes, total {} not parsed)'.format(len(parsed[1]))
            part = parsed[1][0:min(10, len(parsed[1]))]
            print hexlify(part)
    except:
        print("Couldn't parse exp file")


    # 7. Receive photos
    for i in range(6):
        try:
            file_to_download = None
            current_photo_name_sufix = '_{}.jpg'.format(i)
            for f in file_list:
                if f['File'] == file_name + current_photo_name_sufix:
                    file_to_download = f
                    break
            print("Selecting " + str(file_to_download))
            logger.log(file_to_download)

            chunks = downloader.download(file_to_download)
            print("Download file")
            RemoteFileTools.save_chunks(args.experiment_file + current_photo_name_sufix + '.raw', chunks)
            RemoteFileTools.save_photo(args.experiment_file + current_photo_name_sufix, chunks)
        except:
            print("Photo failed")
    print("End...")


