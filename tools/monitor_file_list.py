import argparse
import os
import sys
from datetime import datetime
import pprint

from colorama import Fore, Style, Back
import zmq
from zmq.utils.win32 import allow_interrupt

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
import response_frames
from utils import ensure_byte_list, ensure_string

from remote_files import RemoteFileTools

Decoder = response_frames.FrameDecoder(response_frames.frame_factories)

last_cid = 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('address', nargs='+', help='Address to connect for frames')

    return parser.parse_args()


def connect_sockets(addresses):
    ctx = zmq.Context.instance()
    result = []

    for a in addresses:
        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, '')
        socket.connect(a)

        result.append(socket)

    return result


def parse_frame(raw_frame):
    return Decoder.decode(ensure_byte_list(raw_frame[16:-2]))


def process_frame(already_received, frame):
    global last_cid
    if not isinstance(frame, response_frames.file_system.FileListSuccessFrame):
        return

    if frame.correlation_id != last_cid:
        already_received.clear()
        last_cid = frame.correlation_id
        print("\n\n====================================")
        print("Correlation id: {0}".format(frame.correlation_id))
        print("====================================\n")

    if frame.seq() in already_received:
        return

    file_list = RemoteFileTools.parse_file_list(frame)

    for f in file_list:
        print("{0}:\t{1}".format(f['File'], f['Chunks']))

    already_received.add(frame.seq())


def run(args):
    import colorama
    colorama.init()

    sockets = connect_sockets(args.address)

    abort_push = zmq.Context.instance().socket(zmq.PAIR)
    abort_push.bind('inproc://sail_monitor/abort')
    abort_pull = zmq.Context.instance().socket(zmq.PAIR)
    abort_pull.connect('inproc://sail_monitor/abort')

    already_received = set()

    def abort():
        abort_push.send('ABORT')

    with allow_interrupt(abort):
        while True:
            (read, _, _) = zmq.select(sockets + [abort_pull], [], [])

            if abort_pull is read:
                break

            for ready in read:
                frame = ready.recv()
                frame = parse_frame(frame)
                process_frame(already_received, frame)


run(parse_args())
