import os
import math
import sys
import argparse
import datetime
import md5
import copy

sys.path.append(os.path.join(os.path.dirname(__file__), '../../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from crc import pad, calc_crc
import telecommand


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('file',
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
        assert 0 <= i <= 5, "Incorrect boot slot"
    if boot_slots != [3, 4, 5]:
        print "================ WARNING =============="
        print "===   Boot slots not on fallback!   ==="
        print "======================================="
        print ""
    return boot_slots


args = parse_args()
PART_SIZE = telecommand.WriteProgramPart.MAX_PART_SIZE

binary_data_org = open(args.file, 'rb').read()
binary_data = copy.copy(binary_data_org)
binary_data = list(pad(binary_data, multiply_of=128, pad_with=0x1A))
crc = calc_crc(binary_data)
boot_slots = process_boot_slots(args.boot_slots)

chunks = int(math.ceil(len(binary_data)*1.0/PART_SIZE))

print "Generating:"
print "  - file {}".format(args.file)
print "  - length {} bytes, {} chunks".format(len(binary_data), chunks)
print "  - bootslots {}".format(boot_slots)
print "  - Sample: tc.WriteProgramPart(" + str(boot_slots) + ", 0xA5, [0x00, 0x01])"
print "  - CRC: {:04X}".format(crc)

output_file = open(args.output, 'w')
output_file.write('tasks = [\n')

output_file.write("    # Generated for file {} at {date:%Y-%m-%d %H:%M:%S}, md5sum: {md5}, crc: 0x{crc:04X}\n\n"
                  .format(args.file,
                  date=datetime.datetime.now(),
                  md5=md5.new(binary_data_org).hexdigest(),
                  crc=crc))

mask = 0
not_mask = 0b111111
for i in boot_slots:
    mask |= (1 << i)
    not_mask &= ~(1 << i)


output_file.write("    # Get beacons from deep-sleep\n")
output_file.write("    [[tc.SendBeacon(), 15], SendLoop, WaitMode.NoWait],\n")
output_file.write('\n')

output_file.write("    # Wake-up from deep-sleep\n")
output_file.write("    [[tc.PingTelecommand(), 15], SendLoop, WaitMode.NoWait],\n")
output_file.write('\n')
output_file.write("    [tc.SetBitrate(4, BaudRate.BaudRate9600), Send, WaitMode.Wait],\n")
output_file.write('\n')
output_file.write("    [tc.SendBeacon(), Send, WaitMode.Wait],\n")

output_file.write('\n')
output_file.write('\n')

output_file.write("    [\"The next step is EraseBootTableEntry.\", Print, WaitMode.Wait],\n")
for i in boot_slots:
    output_file.write("    [tc.EraseBootTableEntry([{}]), Send, WaitMode.Wait],\n".format(i))

output_file.write('\n')

output_file.write("    [\"The next step is program upload.\", Print, WaitMode.Wait],\n\n")

chunk = 0
offset = 0
while offset < len(binary_data):
    binary = binary_data[offset:offset + PART_SIZE]
    output_file.write("    [tc.WriteProgramPart({}, {: <3} * 190, {}), Send, WaitMode.Wait],\n".format(
                      str(boot_slots),
                      str(chunk),
                      str('[{}]'.format(', '.join(hex(x) for x in binary)))))

    chunk += 1
    offset = chunk * PART_SIZE

    if chunk % 10 == 0:
        output_file.write("\n")

output_file.write('\n')

output_file.write("    [\"The next step is FinalizeProgramEntry.\", Print, WaitMode.Wait],\n")
output_file.write("    [tc.FinalizeProgramEntry({}, {}, 0x{:04X}, \"name\"), Send, WaitMode.Wait],\n".format(
    boot_slots, len(binary_data), crc))

output_file.write('\n')

output_file.write("    [\"The next step is SetBootSlots.\", Print, WaitMode.Wait],\n")
output_file.write("    [tc.SetBootSlots(76, {}, {}), Send, WaitMode.Wait],\n".format(bin(mask), bin(not_mask)))

output_file.write('\n')

output_file.write("    [\"The next step is Power Cycle B.\", Print, WaitMode.Wait],\n")
output_file.write("    [tc.PowerCycleTelecommand(100), Send, WaitMode.Wait],\n")

output_file.write('\n')

output_file.write("    [\"The satellite shall boot to the new software.\", Print, WaitMode.Wait],\n")
output_file.write("    [tc.PingTelecommand(), Send, WaitMode.Wait],\n")

output_file.write('\n')
output_file.write("    [tc.SendBeacon(), Send, WaitMode.Wait],\n")

output_file.write('\n')
output_file.write("    [[tc.SendBeacon(), 20], SendLoop, WaitMode.NoWait],\n")
output_file.write('\n')

output_file.write(']\n')
output_file.close()
