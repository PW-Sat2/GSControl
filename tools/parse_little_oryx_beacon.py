import imp
import os
import sys
import socket
import re
import struct
import json

sys.path.append(os.path.join(os.path.dirname(
    __file__), '../build/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(
    __file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import timedelta, datetime, date, time

from struct import pack

import response_frames

from bitarray import bitarray
from response_frames.little_oryx import LittleOryxDeepSleepBeacon
from telecommand import *

from emulator.beacon_parser.little_oryx_beacon_parser import LittleOryxBeaconParser
from emulator.beacon_parser.parser import BitReader, BeaconStorage


from utils import ensure_string, ensure_byte_list
import response_frames

class ParseLittleOryxBeacon:
    @staticmethod
    def parse(frame):
        if isinstance(frame, LittleOryxDeepSleepBeacon):
            all_bits = bitarray(endian='little')
            all_bits.frombytes(''.join(map(lambda x: pack('B', x), frame.payload())))
            
            reader = BitReader(all_bits)
            store = BeaconStorage()

            parsers = LittleOryxBeaconParser().GetParsers(reader, store)
            parsers.reverse()

            while len(parsers) > 0:
                parser = parsers.pop()
                parser.parse()

            result = store.storage
        else:
            result = None

        return result

    @staticmethod
    def convert_values(o):
        if isinstance(o, timedelta):
            return o.total_seconds()
        
        if isinstance(o, date):
            return o.strftime("%Y-%m-%d")

        if isinstance(o, time):
            return o.strftime("%H:%M:%S")

        try:
            return {
                'raw': o.raw,
                'converted': o.converted,
                'unit': getattr(o, 'unit') if hasattr(o, 'unit') else None
            }
        except AttributeError:
            return o


    @staticmethod
    def convert(beacon):
        for k, v in beacon.items():
            for k2, v2 in beacon[k].items():
                beacon[k][k2] = ParseLittleOryxBeacon.convert_values(v2)

        return beacon

    @staticmethod
    def convert_json(beacon):
        return json.dumps(beacon, default=ParseLittleOryxBeacon.convert_values, sort_keys=True, indent=4)
    
