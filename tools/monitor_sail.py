import argparse
import os
import sys
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


def display_time(t):
    print '\t', Fore.CYAN, 'Mission time: {}{}{}'.format(Fore.GREEN, t, Fore.GREEN), Style.RESET_ALL


def display_gyro(g):
    x = AngularRate(g['X'])
    y = AngularRate(g['Y'])
    z = AngularRate(g['Z'])
    t = GyroTemperature(g['Temperature'])
    print '\t', Fore.BLUE, 'Gyro', Fore.WHITE, \
        ' X: {4}{0:.2f}{5} Y: {4}{1:.2f}{5} Z: {4}{2:.2f}{5} deg/sec Temperature {4}{3:.2f}{5} C'\
            .format(x.converted, y.converted, z.converted, t.converted,  Fore.GREEN, Fore.WHITE), Style.RESET_ALL


def rtd_to_centigrades(raw):
    return pt1000_res_to_temp((raw / 4096.0 * 1000) / (1 - raw / 4096.0))


def display_sail(s):
    if s['Open']:
        print '\t', Fore.BLACK + Back.WHITE + 'SAIL DEPLOYED!!!!!!1111', Style.RESET_ALL

    t = s['Temperature']

    print '\t', Fore.MAGENTA, 'Sail temperature {1}{0}{2} C'.format(rtd_to_centigrades(t), Fore.GREEN, Fore.WHITE)


def display_experiment_info(exp):
    for entry in exp:
        if entry == 'Synchronization':
            pass
        elif 'time' in entry:
            display_time(entry['time'])
        elif 'Gyro' in entry:
            display_gyro(entry['Gyro'])
        elif 'Sail' in entry:
            display_sail(entry['Sail'])
        elif 'Padding' in entry:
            pass
        else:
            print entry


def process_frame(already_received, frame):
    if not isinstance(frame, response_frames.SailExperimentFrame):
        return

    if frame.seq() in already_received:
        pass

    exp = ExperimentFileParser.parse_partial(ensure_string(frame.payload()))

    print 'Sail experiment chunk {}'.format(frame.seq())
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
