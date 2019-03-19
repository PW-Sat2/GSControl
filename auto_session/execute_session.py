import os.path
import sys
from datetime import datetime, timedelta

import argparse
import zmq

sys.path.append(os.path.join(os.path.dirname(
    __file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


GS_LIST = dict(map(lambda i: (i['name'], i), [
    dict(
        name='elka',
        host='elka-main.gs.pw-sat.pl',
        uplink=7000,
        downlink=7001
    ),
    dict(
        name='fp',
        host='fp-main.gs.pw-sat.pl',
        uplink=7000,
        downlink=7001
    ),
    dict(
        name='flatsat',
        host='flatsat',
        uplink=7000,
        downlink=7001
    )
]))


def parse_args():
    parser = argparse.ArgumentParser()

    def gs_list(v):
        names = v.split(',')
        return map(lambda n: GS_LIST[n], names)

    def gs(v):
        return GS_LIST[v]

    parser.add_argument('--downlink', '-d', type=gs_list, help="Comma separated list of downlink GSes",
                        default=gs_list('elka,fp'))
    parser.add_argument(
        '--config', '-c', help="Config file (Python one)", required=True)
    parser.add_argument('--uplink', '-u', type=gs,
                        help="GS to be used for uplink", required=True)
    parser.add_argument('--scenario', help="Scenario to execute",
                        required=False, default='keep_alive.py')

    return parser.parse_args()


def load_session(file_name):
    scope = {}

    with open(file_name, 'r') as f:
        exec(f, scope)

    return scope['session']


def build_recv_sock(gs):
    context = zmq.Context.instance()
    sock = context.socket(zmq.SUB)
    sock.connect("tcp://%s:%d" % (gs['host'], gs['downlink']))
    sock.setsockopt(zmq.SUBSCRIBE, "")

    return sock


def run(args):
    from radio.radio_sender import Sender
    from auto_session.session_base import SessionScope
    import imp
    cfg = imp.load_source('config', args.config)

    session_file = os.path.join(os.path.dirname(__file__), args.scenario)
    session = load_session(session_file)

    steps = list(session(
        start=datetime.now(),
        stop=datetime.now() + timedelta(minutes=30)
    ))

    sender = Sender(
        source_callsign=cfg.config['COMM_UPLINK_CALLSIGN'],
        port=args.uplink['uplink'],
        target=args.uplink['host']
    )

    receivers = map(build_recv_sock, args.downlink)

    scope = SessionScope(sender, receivers)

    for step in steps:
        step(scope)


run(parse_args())
