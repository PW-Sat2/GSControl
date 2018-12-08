import imp
import os
import sys
import logging

import argparse
import colorlog

cfg_module = imp.new_module('config')
cfg_module.config = dict(
    VALID_CRC='0xBFFD'
)
sys.modules['config'] = cfg_module

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mission_store import MissionStore


def setup_logging():
    root_logger = logging.getLogger()

    handler = colorlog.StreamHandler()

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s: %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)


def run_summary(store, current_session):
    steps_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'summary_steps')
    steps = os.listdir(steps_folder)
    steps = sorted(steps)
    steps = map(lambda f: os.path.join(steps_folder, f), steps)

    session = store.get_session(current_session)

    # create in-memory summary.scope so we can inject values into steps
    # IDE will look in scope.py to detect variables and types
    # try to keep these two in sync
    scope_module = imp.new_module('summary.scope')
    scope_module.session = session
    scope_module.store = store

    sys.modules['summary.scope'] = scope_module

    scope_globals = {
        'store': store,
        'session': session,
    }

    session_step = session.expand_path('summary.py')
    if os.path.exists(session_step):
        steps.append(session_step)
    else:
        logging.warning("No session-specific summary script ({} not found)".format(session_step))

    for step in steps:
        logging.debug('Running step {}'.format(step))
        execfile(step, scope_globals)


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    mission_repo_default = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'mission'))

    parser.add_argument('-m', '--mission', help="Path to mission repository", default=mission_repo_default)
    parser.add_argument('session', help="Session ID (number) to summarise", type=int)

    return parser.parse_args()


def main(args):
    mission_data = os.path.abspath(args.mission)
    store = MissionStore(root=mission_data)
    session = args.session
    run_summary(store, session)


setup_logging()
main(parse_args())
