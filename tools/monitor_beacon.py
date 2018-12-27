import argparse
from datetime import datetime
from pprint import pprint
import colorama
from colorama import Fore

import tableprint
from typing import List, Tuple, Dict
import zmq
from zmq.utils.win32 import allow_interrupt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
import response_frames
from utils import ensure_byte_list, ensure_string

Decoder = response_frames.FrameDecoder(response_frames.frame_factories)


def address_type(v):
    (name, url) = v.split('=')
    return (name, url)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('address', nargs='+', help='Address to connect for frames', type=address_type)

    return parser.parse_args()


def connect_sockets(addresses):
    # type: (List[Tuple[str, str]]) -> Dict[zmq.Socket, str]
    ctx = zmq.Context.instance()
    result = {}

    for (name, address) in addresses:
        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, '')
        socket.connect(address)

        result[socket] = name

    return result


def parse_frame(raw_frame):
    return Decoder.decode(ensure_byte_list(raw_frame[16:-2]))


def ok_color(is_ok):
    if is_ok:
        return colorama.Fore.GREEN
    else:
        return colorama.Fore.RESET


def process_frame(gs, tc, frame):
    # type: (str, tableprint.TableContext, response_frames.BeaconFrame) -> None

    tm = frame._parsed

    tm_comm = tm['11: Comm']
    tm_ctrl_a = tm['14: Controller A']
    tm_ctrl_b = tm['15: Controller B']

    bitrate = str(tm_comm['0591: Transmitter Bitrate'].converted)

    bp_volt_a = tm_ctrl_a['1019: BATC.VOLT_A'].converted
    bp_volt_b = tm_ctrl_b['1204: BATC.VOLT_B'].converted

    bp_temp_a = tm_ctrl_a['1062: BP.Temperature A'].converted
    bp_temp_b = tm_ctrl_a['1075: BP.Temperature B'].converted

    rx_curr = tm_comm['0720: [Now] Receiver Current'].converted
    distr_3v3_curr = tm_ctrl_a['0956: DISTR.CURR_3V3'].converted * 1000

    tc([
        datetime.now().strftime('%H:%M:%S'),
        Fore.RESET + gs,
        ok_color(bitrate == '1200') + bitrate + Fore.RESET,
        '{a_ok}{0:.2f}{reset} {b_ok}{1:.2f}{reset}'.format(
            bp_volt_a,
            bp_volt_b,
            a_ok=ok_color(bp_volt_a > 7.55),
            b_ok=ok_color(bp_volt_b > 7.55),
            reset=Fore.RESET),
        '{a_ok}{0:.3f}{reset} {b_ok}{1:.3f}{reset}'.format(
            bp_temp_a,
            bp_temp_b,
            a_ok=ok_color(bp_temp_a > -5),
            b_ok=ok_color(bp_temp_b > -5),
            reset=Fore.RESET),
        '{ok}{0:.1f}{reset}'.format(
            rx_curr,
            ok=ok_color(rx_curr < 55 or rx_curr > 100),
            reset=Fore.RESET),
        '{ok}{0:.0f}{reset}'.format(
            distr_3v3_curr,
            ok=ok_color(distr_3v3_curr < 60),
            reset=Fore.RESET),
    ])


def run(args):
    colorama.init()

    sockets = connect_sockets(args.address)

    abort_push = zmq.Context.instance().socket(zmq.PAIR)
    abort_push.bind('inproc://sail_monitor/abort')
    abort_pull = zmq.Context.instance().socket(zmq.PAIR)
    abort_pull.connect('inproc://sail_monitor/abort')

    def abort():
        abort_push.send('ABORT')

    counter = 1

    with allow_interrupt(abort):
        with tableprint.TableContext(
                ['Time', 'GS', 'BitRate', 'BP VOLT', 'BP TEMP', 'COMM RX Current', '3V3 DISTR CURRENT'],
                width=20
        ) as tc:
            while True:
                (read, _, _) = zmq.select(sockets.keys() + [abort_pull], [], [])

                if abort_pull is read:
                    break

                for ready in read:
                    gs = sockets[ready]
                    frame = ready.recv()
                    frame = parse_frame(frame)

                    if not isinstance(frame, response_frames.BeaconFrame):
                        continue

                    if counter % 10 == 0:
                        print(tc.headers)

                    counter += 1

                    process_frame(gs, tc, frame)


run(parse_args())
