import os
import math
import sys
import argparse
from base64 import b64decode

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import ensure_byte_list
from radio.radio_frame_decoder import FallbackResponseDecorator
import response_frames
import telecommand as tc

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('downlink_frames',
                        help="Downlink frames with already done uploads (.frames file)")
    parser.add_argument('tasklist', nargs='?',
                        help="Previous tasklist")
    parser.add_argument('-o', '--output', required=False,
                        help="Output tasklist file")

    return parser.parse_args()


args = parse_args()

frame_decoder = FallbackResponseDecorator(response_frames.FrameDecoder(response_frames.frame_factories))

upload_done = []
with open(args.downlink_frames, 'r') as downlink_frames:
    for frame in downlink_frames:
        f = frame_decoder.decode(ensure_byte_list(b64decode(frame.split(',')[2])[16:-2]))

        if isinstance(f, response_frames.EntryProgramPartWriteSuccess):
            upload_done.append((f.offset, f.size, f.entries))

upload_done = sorted(list(set(upload_done)))
print "Confirmed slots: ",
for c in upload_done:
    chunk = c[0] * 1.0 / tc.WriteProgramPart.MAX_PART_SIZE
    if chunk.is_integer():
        chunk = int(chunk)
    print chunk,
print "\n\n"

if args.tasklist is None:
    exit(0)

output = args.output if args.output is not None else args.tasklist

buf = ''
with open(args.tasklist) as tasklist:
    for task in tasklist:
        skip = False

        if task.find('tc.WriteProgramPart(') != -1:
            tec = eval(','.join(task.split(',')[0:-3])[1:])

            requested = (tec._offset, len(tec._content), ord(tec.payload()[0]))
            if requested in upload_done:
                upload_done.remove(requested)
                skip = True

        if skip:
            buf += '#'
            buf += task[1:]
        else:
            buf += task

with open(output, 'w') as output:
    output.write(buf)

if upload_done != []:
    print ""
    print "========================= WARNING =========================="
    print "=== all.frames contain frames which were not requested ! ==="
    print upload_done
    print "============================================================"
    print ""
