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

from radio.radio_frame_decoder import FallbackResponseDecorator
import argparse

from telecommand import *
from response_frames import operation
from devices import comm
import datetime
import pprint
import time

import sys
import progressbar
from Queue import Empty

from math import ceil
from time import time, sleep


from crc import pad, calc_crc
from response_frames.program_upload import EntryEraseSuccessFrame, EntryProgramPartWriteSuccess, EntryFinalizeSuccess
from telecommand import WriteProgramPart, EraseBootTableEntry, FinalizeProgramEntry

frame_decoder = FallbackResponseDecorator(response_frames.FrameDecoder(response_frames.frame_factories))


parser = argparse.ArgumentParser()

parser.add_argument('-c', '--config', required=False,
                    help="Config file (in CMake-generated integration tests format)",
                    default=os.path.join(os.path.dirname(__file__), 'config.py'))
parser.add_argument('-t', '--downlink-host', required=False,
                    help="GNURadio host", default='localhost')
parser.add_argument('-p', '--downlink-port', required=False,
                    help="GNURadio port", default=7001, type=int)
parser.add_argument('-u', '--uplink-host', required=False,
                    help="Uplink host", default='localhost')
parser.add_argument('-v', '--uplink-port', required=False,
                    help="Uplink port", default=7000, type=int)

parser.add_argument('-f', '--file', required=True,
                    help="Bin file")

parser.add_argument('-s', '--slots', nargs='+', required=True,
                    help="List of boot slots", type=int)

parser.add_argument('-d', '--desc', required=True,
                    help="Description of the slot")


args = parser.parse_args()
imp.load_source('config', args.config)
from config import config

sender = Sender(args.uplink_host, args.uplink_port, source_callsign=config['COMM_UPLINK_CALLSIGN'])
receiver = Receiver(args.downlink_host, args.downlink_port)
receiver.timeout(1)



PARTS_PER_ITERATION = 1

def wait_for_frame(expected_type, timeout):
    start_time = time()
    timeout_at = start_time + timeout

    while time() < timeout_at:
        try:
            data = receiver.receive_no_wait()
            if data is not None:
                data = receiver.decode_kiss(data)
                frame = frame_decoder.decode(data)

                if type(frame) is expected_type:
                    pprint.pprint(frame)
                    #sleep(5)
                    return frame
                print 'Ignoring'
        except Empty:
            pass

    return None


file = args.file
slots = args.slots
description = args.desc

with open(file, 'rb') as f:
    program_data = f.read()

program_data = pad(program_data, multiply_of=128, pad_with=0x1A)
crc = calc_crc(program_data)
length = len(program_data)
parts = int(ceil(length / float(WriteProgramPart.MAX_PART_SIZE)))

print 'Will upload {} bytes of program (CRC: {:4X}), {} parts into slots {}'.format(
    length,
    crc,
    parts,
    slots
)

print 'Erasing boot slots'

sender.send(EraseBootTableEntry(slots))

response = wait_for_frame(EntryEraseSuccessFrame, 50)
if response is None:
    print 'Failed to erase'
    sys.exit(1)
print 'Boot slots erased'


print 'Uploading program'
offsets = range(0, length, WriteProgramPart.MAX_PART_SIZE)
total_parts = len(offsets)

with progressbar.ProgressBar(max_value=total_parts, redirect_stdout=True) as bar:
    bar.update(0)
    while len(offsets) > 0:
        count = 0
        print 'Sending offset: {}'.format(offsets[0])
        while True:
            count += 1
            print 'Trial: {}'.format(count)
            part = program_data[offsets[0]:offsets[0] + WriteProgramPart.MAX_PART_SIZE]
            sender.send(WriteProgramPart(entries=slots, offset=offsets[0], content=part))
            response = wait_for_frame(EntryProgramPartWriteSuccess, 10)
            try:
                if response.offset not in offsets:
                    print 'Invalid offset received {}'.format(response.offset)
                else:
                    offsets.remove(response.offset)
                    bar.update(total_parts - len(offsets))
                    break
            except:
                print 'Timeout?'
  

print 'Upload finished'

print 'Finalizing'
for i in range(10):
    try:
        sender.send(FinalizeProgramEntry(slots, length, crc, description))
        response = wait_for_frame(EntryFinalizeSuccess, 500)
    except:
        pass

    if response is None:
        print 'Failed to finalize - try no. {0}'.format(i)
    else:
        break

print 'Uploaded {} bytes of program (CRC: {:4X}), {} parts into slots {}'.format(
    length,
    crc,
    parts,
    slots
)
