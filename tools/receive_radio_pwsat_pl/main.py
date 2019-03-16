import argparse
from receiver import Receiver
from make_frame_object import make_frame_object
import sys
import time
import traceback
import datetime


parser = argparse.ArgumentParser()

parser.add_argument('-t', '--target', required=False,
                    help="Target", default='wss://radio.pw-sat.pl/communication/log/ws')
parser.add_argument('-o', '--origin', required=False,
                    help="Origin", default='https://radio.pw-sat.pl/')

args = parser.parse_args()


rcv = Receiver(target=args.target, origin=args.origin)
rcv.open_ws()

counter = 0
while True:
    try:
        raw = rcv.get()
        frame_string_view = make_frame_object(raw)
        counter += 1
        print("{} {:3d} {}".format(datetime.datetime.now().time().strftime('%H:%M:%S'), counter, frame_string_view))
    except Exception:
        rcv.open_ws()
        time.sleep(0.1)
