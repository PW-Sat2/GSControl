import os.path
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from radio.radio_sender import Sender
from auto_session.session_base import SessionScope

# TODO: GS array
# TODO: Receiver thread per step
# TODO: Some context to hold all received/uplinked frames
# TODO: Load config
# TODO: Connect all receivers


def load_session(file_name):
    scope = {}

    with open(file_name, 'r') as f:
        exec (f, scope)

    return scope['session']


def run():
    session_file = os.path.join(os.path.dirname(__file__), 'keep_alive.py')
    session = load_session(session_file)

    steps = list(session(
        start=datetime.now(),
        stop=datetime.now() + timedelta(minutes=5)
    ))

    sender = Sender(source_callsign='SP9NOV', port=7000, target='flatsat')

    scope = SessionScope(sender)

    for step in steps:
        step(scope)


import imp
imp.load_source('config', 'C:/PW-Sat/obc-build/integration_tests/config.py')

run()
