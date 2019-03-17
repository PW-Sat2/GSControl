import sys
import os
import logging
import time
import datetime
from pprint import pformat
import json
import struct


sys.path.append(os.path.join(os.path.dirname(__file__), 'GSControl/PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'GSControl'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


from radio.radio_frame_decoder import *
from tools.remote_files import RemoteFileTools
from utils import ensure_string, ensure_byte_list
from devices import comm_beacon
import response_frames

from datetime import timedelta, datetime, date, time

from struct import pack

import response_frames

from bitarray import bitarray
from devices import comm_beacon
from telecommand import *
from math import ceil
import re


from emulator.beacon_parser.full_beacon_parser import FullBeaconParser
from emulator.beacon_parser.parser import BitReader, BeaconStorage

class ParseBeacon:
    @staticmethod
    def parse(frame):
        print type(frame)
        if isinstance(frame, comm_beacon.BeaconFrame):
            all_bits = bitarray(endian='little')
            all_bits.frombytes(''.join(map(lambda x: pack('B', x), frame.payload())))
            
            reader = BitReader(all_bits)
            store = BeaconStorage()

            parsers = FullBeaconParser().GetParsers(reader, store)
            parsers.reverse()

            while len(parsers) > 0:
                parser = parsers.pop()
                parser.parse()

            result = store.storage
        else:
            result = frame

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
                beacon[k][k2] = ParseBeacon.convert_values(v2)

        return beacon

    @staticmethod
    def convert_json(beacon):
        return json.dumps(beacon, default=ParseBeacon.convert_values, sort_keys=True, indent=4)

    @staticmethod
    def parse_file_list(frame):
        if isinstance(frame, response_frames.file_system.FileListSuccessFrame):
            res = bytearray(frame.payload())[2:]

            file_list = []
            
            while True:
                now = res.find('\x00')
                if now == -1:
                    return file_list
                
                name = str(res[:now])
                size = struct.unpack('<I', res[now+1:now+5])[0]
                chunks = int(ceil(size/230.))

                file_list.append({'File': name, 'Size': size, 'Chunks': chunks})
                res = res[now+5:]
        else:
            file_list = None

        return file_list

decoder = response_frames.FrameDecoder(response_frames.frame_factories)

def make_frame_object(data):
    packet = json.loads(data)
    decoded_frame = _create_frame_object(packet['bytes'])

    if isinstance(decoded_frame, comm_beacon.BeaconFrame):
        becon = ParseBeacon.convert(ParseBeacon.parse(decoded_frame))
        sc_a = becon['14: Controller A']['1088: Safety Counter']
        pc_a = becon['14: Controller A']['1096: Power Cycle Count']
        sc_b = becon['15: Controller B']['1214: Safety Counter']
        pc_b = becon['15: Controller B']['1222: Power Cycle Count']
        return "Safety counter A/B: {0}, {1}\r\n Power Cycle A/B: {2}, {3}".format(sc_a, sc_b, pc_a, pc_b)

    elif isinstance(decoded_frame, response_frames.file_system.FileListSuccessFrame):
        decoded_frame =  ParseBeacon.parse_file_list(decoded_frame)

    return pformat(decoded_frame)

def _create_frame_object(frame_data):
    def uint(num):
        return num + 256 if num < 0 else num

    uint_data = map(uint, frame_data)
    return _parse_packet(uint_data)

def _parse_packet(frame_data):
    return decoder.decode(ensure_byte_list(frame_data[17:-2]))
