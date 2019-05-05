import argparse
from receiver import Receiver
from make_frame_object import make_frame_object, get_userId
from callsign_decoder import CallsignDecoder
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
parser.add_argument('-c', '--callsign-file', required=False, help="Callsigns JSON file", default=False)
parser.add_argument('-d', '--debug', required=False, action='store_true',
                    help="Debug", default=False)                    

args = parser.parse_args()

colorama.init()
callsign_decoder = CallsignDecoder(args.callsign_file)

rcv = Receiver(target=args.target, origin=args.origin)
rcv.open_ws()

print("Listening on websocket...")

counter = 0
while True:
    try:
        raw = rcv.get()

        if args.debug:
            print(raw)

        frame_string_view = make_frame_object(raw)
        counter += 1
        userId = get_userId(raw)
        callsign = callsign_decoder.decode(userId)

        timestamp_str = '{}{}{}'.format(colorama.Fore.CYAN, datetime.datetime.now().time().strftime('%H:%M:%S'), colorama.Fore.RESET)
        counter_str = '{}{:3d}{}'.format(colorama.Fore.BLACK + colorama.Style.BRIGHT, counter, colorama.Fore.RESET + colorama.Style.RESET_ALL)
        callsign_str  = ''
        if callsign:
            callsign_str = '{}{:7s}{} '.format(colorama.Fore.BLUE, callsign, colorama.Fore.RESET)

        print("{} {} {}{}".format(timestamp_str, counter_str, callsign_str, frame_string_view))
    except KeyboardInterrupt:
        print("Ctrl+C received. Ending...")
        break
    except Exception:
        rcv.open_ws()
        time.sleep(0.1)
