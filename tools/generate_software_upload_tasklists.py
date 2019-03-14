import os
import math
import sys
import argparse
import json

import numpy as np
import datetime as dt

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import telecommand
# telecommand.WriteProgramPart()


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--file', required=True,
                        help=".bin file to upload")
    parser.add_argument('-c', '--chunks-per-tc', required=False,
                        help="Maximum chunks allowed for download with single telecommand", default=20, type=int)
    parser.add_argument('-o', '--output', required=False,
                        help="Output file path", default='tasklist.software_upload.py')

    parser.add_argument('-b', '--boot-slots', nargs='+', help='Boot slots to upload to. Default - 3, 4, 5', required=False,
                        default=['3', '4', '5'])

    return parser.parse_args()


def process_boot_slots(boot_slots):
    boot_slots = [int(i) for i in boot_slots]
    for i in boot_slots:
        assert 1 <= i <= 6, "Incorrect boot slot"
    if boot_slots != [3, 4, 5]:
        print "================ WARNING =============="
        print "===   Boot slots not on fallback!   ==="
        print "======================================="
        print ""
    return boot_slots


args = parse_args()
PART_SIZE = telecommand.WriteProgramPart.MAX_PART_SIZE

binary_data = open(args.file, 'rb').read()
boot_slots = process_boot_slots(args.boot_slots)

print PART_SIZE
chunks = int(math.ceil(len(binary_data)*1.0/PART_SIZE))

print "Generating:"
print "  - file {}".format(args.file)
print "  - length {} bytes, {} chunks".format(len(binary_data), chunks)
print "  - bootslots {}".format(boot_slots)
print "  - Sample: tc.WriteProgramPart(" + str(boot_slots) + ", 0xA5, [0x00, 0x01])"

output_file = open(args.output, 'w')
output_file.write('tasks = [\n')

offset = 0
while offset < len(binary_data):
    bin = binary_data[offset:offset + PART_SIZE]
    output_file.write("[tc.WriteProgramPart({}, {}, {}), Send, WaitMode.Wait],\n".format(
                      str(boot_slots),
                      str(offset),
                      str('[{}]'.format(', '.join(hex(ord(x)) for x in bin)))))

    offset += PART_SIZE

output_file.write(']\n')
output_file.close()