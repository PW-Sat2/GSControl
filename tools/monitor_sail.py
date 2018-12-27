import argparse
import os
import sys
from datetime import datetime

from colorama import Fore, Style, Back
import zmq
from zmq.utils.win32 import allow_interrupt

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
import response_frames
from utils import ensure_byte_list, ensure_string
from experiment_file import ExperimentFileParser
from emulator.beacon_parser.gyroscope_telemetry_parser import AngularRate, GyroTemperature
from emulator.beacon_parser.resistance_sensors import pt1000_res_to_temp

Decoder = response_frames.FrameDecoder(response_frames.frame_factories)


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


def rtd_to_centigrades(raw):
    return pt1000_res_to_temp((raw / 4096.0 * 1000) / (1 - raw / 4096.0))


def display_experiment_info(exp):
    last_entry = {}

    def all_in():
        required = ['time', 'Gyro', 'Sail']

        return all(map(lambda x: x in last_entry, required))

    for entry in exp:
        if entry == 'Synchronization':
            pass
        elif 'time' in entry:
            last_entry.clear()
            last_entry.update(entry)
        elif 'Gyro' in entry:
            last_entry.update(entry)
        elif 'Sail' in entry:
            last_entry.update(entry)
        elif 'Padding' in entry:
            pass
        else:
            print entry

        if all_in():
            try:
                print("X: {0:4.2f} \t Y: {1:4.2f} \t Z: {2:4.2f} */s \t {3} \t {4:2.1f} *C".format(
                    AngularRate(last_entry['Gyro']['X']).converted,
                    AngularRate(last_entry['Gyro']['Y']).converted,
                    AngularRate(last_entry['Gyro']['Z']).converted,
                    "SAIL OPEN" if last_entry['Sail']['Open'] else "SAIL NOT OPEN",
                    rtd_to_centigrades(last_entry['Sail']['Temperature'])))
            except:
                print("Exception!")



def process_frame(already_received, frame):
    if not isinstance(frame, response_frames.SailExperimentFrame):
        return

    if frame.seq() in already_received:
        return

    exp = ExperimentFileParser.parse_partial(ensure_string(frame.payload()))

    print '{:%H:%M:%S} Sail experiment chunk {}'.format(datetime.now(), frame.seq())
    display_experiment_info(exp[0])
    print Style.RESET_ALL

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
