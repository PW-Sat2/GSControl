import imp
import os
import sys
import zmq
import string
import random

sys.path.append(os.path.join(os.path.dirname(
    __file__), '../build/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(
    __file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import response_frames
from binascii import hexlify
from experiment_file import ExperimentFileParser
from utils import ensure_string

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
import logging
from radio.radio_frame_decoder import *

import binascii
import struct

if __name__ == '__main__':
    filePath = sys.argv[1]
    with open(filePath, 'r') as f:
        lines = f.readlines()

    result = []

    for rawSingleResponse in lines:

        rawBase64Data = rawSingleResponse.split(',')[2]
        decodedFrame = binascii.a2b_base64(rawBase64Data)

        decoder = response_frames.FrameDecoder(
            response_frames.frame_factories)

        decoded_frame = decoder.decode(decodedFrame[16:])

        result.append(decoded_frame)

    print len(result)
