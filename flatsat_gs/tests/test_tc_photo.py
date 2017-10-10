import imp
import os
import sys
import zmq
import string
import random

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
import telecommand as tc

# Experiment settings

def get_beacon():
    try:
        sender.send(SendBeacon())
        recv = receiver.receive_frame()
        return recv
    except zmq.Again:
        return None

def take_pictures(camera, resolution, qty, delay, filename_base):
    busy = True
    file_list = None
    while busy:
        print("Requesting photo {}, {}, {}, {}, {}".format(str(camera), str(resolution), qty, delay, filename_base))
        try:
            sender.send(tc.photo.TakePhotoTelecommand(10, camera, resolution, qty, delay, filename_base))
            recv = receiver.receive_frame()
            print(recv)
            if isinstance(recv, common.PhotoSuccessFrame):
                logger.log(recv.payload())
                busy = False
                print("PhotoSuccessFrame received")
        except:
            print "Timeout or other exception"

    time.sleep(20)

    busy = True
    while busy:
        print("Waiting for photo file...")
        try:
            sender.send(ListFiles(13, '/'))
            recv = receiver.receive_frame()
            print(recv)

            file_list = []
            if isinstance(recv, common.FileListSuccessFrame):
                file_list = RemoteFileTools.parse_file_list(recv)
                logger.log(file_list)
                print("File list taken, analyzing...")

                for f in file_list:
                    if f['File'] == "{}_{}".format(filename_base, qty-1):
                        busy = False
                        break

            time.sleep(20)

        except:
            print "Timeout or other exception!"

    return file_list


def test_size(qty, file_list, filename_base):

    # prepare list of files [photos] to be evaluated
    to_check = [filename_base + str("_") + str(i) for i in range(qty)]
    # list of dicts of files to be downloaded
    to_check_dicts = []

    for td in to_check:
        try:
            to_check_dicts.append(filter(lambda filename: filename['File'] == td, file_list))
        except:
            print("Could not find {}".format(td))

    # qty in reality
    real_qty = len(to_check_dicts)

    failed_photos = []
    try:
        failed_photos.append(filter(lambda photosize: photosize['Size'] == 7, to_check_dicts))
    except:
        print("Could not find any failed photos...")

    failed_qty = len(failed_photos)

    return {'real qty': real_qty, 'failed qty': failed_qty, 'failed photos': failed_photos}


def test(camera, resolution, qty, time, results_file):
    name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    file_list = take_pictures(camera, resolution, qty, time, name)
    ret = test_size(qty, file_list, name)
    data = {'time': str(datetime.datetime.now().isoformat()), 'camera' : str(camera), 'resolution': str(resolution), 'time': str(time), 'results': ret}
    pprint.pprint(data, results_file)
    return data


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True,
                        help="Log file path")
    args = parser.parse_args()

    sender = Sender()
    receiver = Receiver()
    receiver.timeout(10000)

    logger = SimpleLogger(args.file + '.log')
    results_file = open(args.file + '_results.log', 'a')

    logger.log('Start of the script')

    # 0. Save experiment settings to log file
    logger.log('Photo Experiment')

    ### TESTS ###
    cams = [CameraLocation.Wing, CameraLocation.Nadir]
    resolutions = [PhotoResolution.p128, PhotoResolution.p240, PhotoResolution.p480]

    '''
    for i in range(5):
        logger.log('Iteration {}'.format(i))
        for cam in cams:
            for resolution in resolutions:
                logger.log('Requesting cam: {}, res: {}, qty: {}, delay: {}, filename: {}'.format(str(cam), str(resolution), 5, 0, results_file))
                r = test(cam, resolution, 5, datetime.timedelta(0), results_file)
                pprint.pprint(r)
    '''

    logger.log('Test photos in time')
    for cam in cams:
        r = test(cam, PhotoResolution.p128, 5, datetime.timedelta(hours=1), results_file)
        pprint.pprint(r)

    logger.log('Finish Photo Experiment')
