import argparse
from receiver import Receiver
from make_frame_object import make_frame_object, get_userId
from callsign_decoder import CallsignDecoder
import sys
import time
import traceback
import datetime
import colorama
import threading


parser = argparse.ArgumentParser()

parser.add_argument('-t', '--target', required=False,
                    help="Target", default='wss://radio.pw-sat.pl/communication/log/ws')
parser.add_argument('-o', '--origin', required=False,
                    help="Origin", default='https://radio.pw-sat.pl/')
parser.add_argument('-c', '--callsign-file', required=False, help="Callsigns JSON file", default=False)
parser.add_argument('-d', '--debug', required=False, action='store_true',
                    help="Debug", default=False)
parser.add_argument('-a', '--all_frames', required=False, action='store_true',
                    help="All frames / turn off GS filtering", default=False)                                      

args = parser.parse_args()
colorama.init()

class HamRadioFrameListener(Receiver):
    def __init__(self, args, callsign_decoder, target="wss://radio.pw-sat.pl/communication/log/ws", origin="https://radio.pw-sat.pl/"):
        super(HamRadioFrameListener, self).__init__(target, origin)
        self.counter = 0
        self.args = args
        self.callsign_decoder = callsign_decoder

    def reset_counter(self):
        self.counter = 0

    def _on_message(self, raw_message):
        try:
            if self.args.debug:
                print(raw_message)

            userId = get_userId(raw_message)
            if not self.args.all_frames and self.callsign_decoder.is_on_black_list(userId):
                return

            frame_string_view = make_frame_object(raw_message)
            self.counter += 1
            callsign = self.callsign_decoder.decode(userId)

            timestamp_str = '{}{}{}'.format(colorama.Fore.CYAN, datetime.datetime.now().time().strftime('%H:%M:%S'), colorama.Fore.RESET)
            counter_str = '{}{:3d}{}'.format(colorama.Fore.BLACK + colorama.Style.BRIGHT, self.counter, colorama.Fore.RESET + colorama.Style.RESET_ALL)
            callsign_str  = ''
            if callsign:
                callsign_str = '{}{:7s}{} '.format(colorama.Fore.BLUE, callsign, colorama.Fore.RESET)

            print("{} {} {}{}".format(timestamp_str, counter_str, callsign_str, frame_string_view))
        except Exception:
            traceback.print_exc()

    def _worker_thread(self):
        self.run_forever()

    def run(self):
        listener_thread = threading.Thread(target=self._worker_thread)
        listener_thread.start()
        return listener_thread


callsign_decoder = CallsignDecoder(args.callsign_file)
listener = HamRadioFrameListener(args=args, callsign_decoder=callsign_decoder, target=args.target, origin=args.origin)
listener_thread = listener.run()
time.sleep(0.1)

while listener_thread.isAlive():
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        listener.shutdown()
        break

print("Ending...")
listener_thread.join()