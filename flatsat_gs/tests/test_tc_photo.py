import imp
import os
import sys
import zmq

sys.path.append(os.path.join(os.path.dirname(__file__), '../build/integration_tests'))
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
from response_frames import common
from devices import comm
from devices.camera import *
from tools.tools import SimpleLogger
import datetime
import pprint
import time

# Experiment settings
correlation_id = 2
delay = datetime.timedelta(0)
file_name_base = 'photo_test_20171009_1300'

def get_beacon():
    try:
        sender.send(SendBeacon())
        recv = receiver.receive_frame()
        return recv
    except zmq.Again:
        return None

def take_picture(camera, resolution, qty, delay, filename_base):
    while True:
        print("Requesting photo {}, {}, {}, {}, {}".format(str(camera), str(resolution), qty, delay, filename_base))
        recv = send_receive(tc.photo.TakePhotoTelecommand(10, camera, resolution, qty, delay, "filename_base"))
        if isinstance(recv, common.PhotoSuccessFrame):
            logger.log(recv.payload())
            break
        print("PhotoSuccessFrame received")

    time.sleep(5)

    while True:
        print("Waiting for photo file")
        sender.send(ListFiles(13, '/'))
        recv = receiver.receive_frame()
        print(recv)

        file_list = []
        if isinstance(recv, common.FileListSuccessFrame):
            file_list = RemoteFileTools.parse_file_list(recv)
            logger.log(file_list)
            print("File list taken, analyzing")

            file_to_be_present = None
            for f in file_list:
                if f['File'] == "{}_{}".format(filename_base, qty-1):
                    file_to_be_present = f
                    break
            if file_to_be_present != None:
                break


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--file', required=True,
                        help="Log file path")

    args = parser.parse_args()

    sender = Sender()
    receiver = Receiver()
    receiver.timeout(10000)
    logger = SimpleLogger(args.file)
    logger.log('Start of the script')

    # 0. Save experiment settings to log file
    logger.log('Photo Experiment')

    take_picture(CameraLocation.Wing, PhotoResolution.p128, 0, delay, 'script')

    '''
    # 1. receive beacon to see the state of sat before experiment
    print("#1. receive beacon to see the state of sat before experiment")
    logger.log("#1. receive beacon to see the state of sat before experiment")
    while True:
        recv = get_beacon()
        print(recv)

        if isinstance(recv, comm.BeaconFrame):
            break

    beacon = ParseBeacon.parse(recv)
    logger.log('Telemetry before experiment')
    logger.log(beacon)

    # 2. send telecommand to turn on experiment
    print("#2. send telecommand to turn on experiment")
    logger.log("#2. send telecommand to turn on experiment")

    while True:
        sender.send(PerformSunSExperiment(correlation_id, gain, itime, samples_count, short_delay, session_count, long_delay, file_name))
        recv = receiver.receive_frame()
        if isinstance(recv, common.ExperimentSuccessFrame):
            logger.log(recv.payload())
            break

    # 3. receive, save and parse incomming frames
    count_beacons = 0
    while True:
        print("#3. receive, save and parse incomming frames")
        recv = get_beacon()
        print(recv)
        time.sleep(5)

        if isinstance(recv, comm.BeaconFrame):
            beacon = ParseBeacon.parse(recv)
            pprint.pprint(beacon['09: Experiments'])
            logger.log(beacon)
            count_beacons += 1

            if (count_beacons > 2) and (str(beacon['09: Experiments']['0484: Current experiment code']) == 'None'):
                print("Finishing #3.")
                break
            else:
                print(count_beacons)
                print(str(beacon['09: Experiments']['0484: Current experiment code']))
                print(type(beacon['09: Experiments']['0484: Current experiment code']))

        if isinstance(recv, common.ExperimentSuccessFrame):
            logger.log(recv.payload())

    time.sleep(60)

    # 4. List files
    while True:
        print("#4. list files")
        sender.send(ListFiles(13, '/'))
        recv = receiver.receive_frame()
        print(recv)

        file_list = []
        if isinstance(recv, common.FileListSuccessFrame):
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
    RemoteFileTools.save_chunks(args.experiment_file + '.txt', merged)

    parsed = ExperimentFileParser.parse_partial(ensure_string(merged))
    with open(file_name + "_parsed.txt", 'w') as f:
        for p in parsed[0]:
            pprint.pprint(p, f)

    if len(parsed[1]) > 0:
        print 'Remaining data (first 10 bytes, total {} not parsed)'.format(len(parsed[1]))
        part = parsed[1][0:min(10, len(parsed[1]))]
        print hexlify(part)


    # 6. Download and save file - secondary
    file_to_download = None
    for f in file_list:
        if f['File'] == file_name + "_sec":
            file_to_download = f
            break
    print("Selecting " + str(file_to_download))
    logger.log(file_to_download)

    downloader = RemoteFile(sender, receiver)

    chunks = downloader.download(file_to_download)
    merged = RemoteFileTools.merge_chunks(chunks)
    print("Download file")
    RemoteFileTools.save_chunks(args.experiment_file + '_sec.txt', merged)

    parsed = ExperimentFileParser.parse_partial(ensure_string(merged))
    with open(file_name + "_sec_parsed.txt", 'w') as f:
        for p in parsed[0]:
            pprint.pprint(p, f)

    if len(parsed[1]) > 0:
        print 'Remaining data (first 10 bytes, total {} not parsed)'.format(len(parsed[1]))
        part = parsed[1][0:min(10, len(parsed[1]))]
        print hexlify(part)
    print("End...")
    

    # 7. Dowload telemetry files
    file_to_download = None
      for f in file_list:
        if f['File'] == "telemetry.current":
            file_to_download = f
            break
    print("Selecting " + str(file_to_download))
    logger.log(file_to_download)
    chunks = downloader.download(file_to_download)
    merged = RemoteFileTools.merge_chunks(chunks)
    print("Download file")
    RemoteFileTools.save_chunks(args.experiment_file + '_telemetry.current.raw', merged)  
    print("Done")  
    '''
