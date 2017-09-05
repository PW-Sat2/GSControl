import imp
import os
import sys
import socket
import re
import struct

from struct import pack

import response_frames

from bitarray import bitarray
from devices import comm
from telecommand import *

from emulator.beacon_parser.full_beacon_parser import FullBeaconParser
from emulator.beacon_parser.parser import BitReader, BeaconStorage

from conversion.comm_conversion import *
from conversion.controller_a_conversions import *
from conversion.controller_b_conversions import *

from utils import ensure_string, ensure_byte_list
import response_frames

class ParseBeacon:
    @staticmethod
    def parse(frame):
        if isinstance(frame, comm.BeaconFrame):
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
            result = None

        return result

    @staticmethod
    def convert(beacon):
        comm = beacon['10: Comm']
        for key, value in comm.items():
            comm[key] = comm_formulas[key](comm[key])
        beacon['10: Comm'] = comm

        controller_a = beacon['13: Controller A']
        for key, value in controller_a.items():
            controller_a[key] = controller_a_formulas[key](controller_a[key])
        beacon['13: Controller A'] = controller_a

        controller_b = beacon['14: Controller B']
        for key, value in controller_b.items():
            controller_b[key] = controller_b_formulas[key](controller_b[key])
        beacon['14: Controller B'] = controller_b

        return beacon
    