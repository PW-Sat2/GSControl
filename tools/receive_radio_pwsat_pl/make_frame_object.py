import sys
import os
import logging
import time
import datetime
from pprint import pformat
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'GSControl/PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'GSControl'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


from radio.radio_frame_decoder import *
from tools.remote_files import RemoteFileTools
from utils import ensure_string, ensure_byte_list

decoder = response_frames.FrameDecoder(response_frames.frame_factories)

def make_frame_object(data):
    packet = json.loads(data)
    decoded_frame = _create_frame_object(packet['bytes'])
    return pformat(decoded_frame)

def _create_frame_object(frame_data):
    def uint(num):
        return num + 256 if num < 0 else num

    uint_data = map(uint, frame_data)
    return _parse_packet(uint_data)

def _parse_packet(frame_data):
    return decoder.decode(ensure_byte_list(frame_data[17:-2]))

def get_userId(data):
    packet = json.loads(data)
    return packet['userId']
