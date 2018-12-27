import argparse
from base64 import b64decode

import progressbar
import zmq
import time


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Frames file to replace')
    parser.add_argument('port', help='ZMQ output port', type=int)
    parser.add_argument('--loop', help='Reply in loop', action='store_true')
    return parser.parse_args()


def run(args):
    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.PUB)
    socket.bind("tcp://%s:%d" % ('*', args.port))

    with open(args.file) as f:
        lines = f.readlines()

        finished = False

        while not finished:
            for line in progressbar.progressbar(lines):
                frame = line.split(',')[2]
                frame = b64decode(frame)
                socket.send(frame)
                time.sleep(1)

            finished = True and not args.loop



run(parse_args())