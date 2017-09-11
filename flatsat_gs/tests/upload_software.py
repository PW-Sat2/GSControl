import imp
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../build/integration_tests'))
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

import sys
import progressbar
from Queue import Empty

from math import ceil
from time import time, sleep


from crc import pad, calc_crc
from response_frames.program_upload import EntryEraseSuccessFrame, EntryProgramPartWriteSuccess, EntryFinalizeSuccess
from telecommand import WriteProgramPart, EraseBootTableEntry, FinalizeProgramEntry

PARTS_PER_ITERATION = 1

sender = Sender('localhost', 8001)
sender.connect()
receiver = Receiver('localhost', 52001)
receiver.connect()
receiver.timeout(1)


def wait_for_frame(expected_type, timeout):
    start_time = time()
    timeout_at = start_time + timeout

    while time() < timeout_at:
        try:
            frame = receiver.receive_no_wait()
            if frame is not None:
                frame = receiver.decode_kiss(frame)
                frame = receiver.make_frame(frame)

            if type(frame) is expected_type:
                return frame

            print 'Ignoring {}'.format(frame)
        except Empty:
            pass

    return None


file = sys.argv[1]
slots = [int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])]
description = sys.argv[5]

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

response = wait_for_frame(EntryEraseSuccessFrame, 20)
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
        while True:
            part = program_data[offsets[0]:offsets[0] + WriteProgramPart.MAX_PART_SIZE]
            sender.send(WriteProgramPart(entries=slots, offset=offsets[0], content=part))
            response = wait_for_frame(EntryProgramPartWriteSuccess, 5)
            try:
                if response.offset not in offsets:
                    print 'Invalid offset received {}'.format(response.offset)
                else:
                    offsets.remove(response.offset)
                    bar.update(total_parts - len(offsets))
                    break
            except:
                print 'Timeout?'
  
    #
    # for i in xrange(0, len(offsets)):
    #     offset = offsets[i]
    #     print 'Uploading to offset 0x{:X} ({}/{})'.format(offset, i + 1, len(offsets))
    #
    #     part = program_data[offset:offset + WriteProgramPart.MAX_PART_SIZE]
    #
    #     sender.send(WriteProgramPart(entries=slots, offset=offset, content=part))
    #
    #     response = wait_for_frame(EntryProgramPartWriteSuccess, 120)
    #
    #     if response is None:
    #         print 'Failed to program'
    #         sys.exit(2)
    #

print 'Upload finished'

print 'Finalizing'
sender.send(FinalizeProgramEntry(slots, length, crc, description))

response = wait_for_frame(EntryFinalizeSuccess, 240)

if response is None:
    print 'Failed to finalize'
    sys.exit(3)

print 'Uploaded {} bytes of program (CRC: {:4X}), {} parts into slots {}'.format(
    length,
    crc,
    parts,
    slots
)
