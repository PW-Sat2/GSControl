import websocket
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(
    __file__), '../build/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(
    __file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from radio.radio_frame_decoder import *

import binascii

import logging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger('websockets')
#logger.setLevel(logging.DEBUG)

decoder = response_frames.FrameDecoder(response_frames.frame_factories)

def open_ws():
    return websocket.create_connection(
        'wss://radio.pw-sat.pl/communication/log/ws',
        origin='https://radio.pw-sat.pl/'
    )

def hello():
    while True:
        ws = open_ws()
        greeting = ws.recv()

        frame = json.loads(greeting)
        if frame['frame'].find('PWSAT2') != -1:
            print("Callsign ok")
        else:
            print("Callsign incorrect")

        data_hex = frame['hex'][:-4]
        data_hex_chopped = data_hex.strip().split(' ')

        data_int = [int(i, 16) for i in data_hex_chopped][17:-2]
        decoded_frame = decoder.decode(data_int)
        print(decoded_frame)

hello()