import argparse
from receiver import Receiver
from make_frame_object import make_frame_object
import sys
import time
import traceback
import datetime
import colorama


parser = argparse.ArgumentParser()

parser.add_argument('-t', '--target', required=False,
                    help="Target", default='wss://radio.pw-sat.pl/communication/log/ws')
parser.add_argument('-o', '--origin', required=False,
                    help="Origin", default='https://radio.pw-sat.pl/')

args = parser.parse_args()

colorama.init()

rcv = Receiver(target=args.target, origin=args.origin)
rcv.open_ws()
print("Listening on websocket...")

counter = 0
while True:
    try:
        raw = rcv.get()
        frame_string_view = make_frame_object(raw)
        counter += 1

        timestamp_str = '{}{}{}'.format(colorama.Fore.CYAN, datetime.datetime.now().time().strftime('%H:%M:%S'), colorama.Fore.RESET)
        counter_str = '{}{:3d}{}'.format(colorama.Fore.BLACK + colorama.Style.BRIGHT, counter, colorama.Fore.RESET + colorama.Style.RESET_ALL)

        print("{} {} {}".format(timestamp_str, counter_str, frame_string_view))
    except KeyboardInterrupt:
        print("Ctrl+C received. Ending...")
        break
    except Exception:
        rcv.open_ws()
        time.sleep(0.1)
