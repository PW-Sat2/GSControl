import imp
import os
import sys

cfg_module = imp.new_module('config')
cfg_module.config = dict(
    VALID_CRC='0xBFFD'
)
sys.modules['config'] = cfg_module

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mission_store import MissionStore


def run_summary(store, current_session):
    steps_folder = os.path.join(os.path.dirname(__file__), 'summary_steps')
    steps = os.listdir(steps_folder)
    steps = sorted(steps)
    steps = map(lambda f: os.path.join(steps_folder, f), steps)

    session = store.get_session(current_session)

    scope_globals = {
        'store': store,
        'session': session,
    }
    for step in steps:
        print 'Running step {}'.format(step)
        execfile(step, scope_globals)


def main():
    mission_data = os.path.abspath('../mission')
    store = MissionStore(root=mission_data)
    session = 16
    run_summary(store, session)


main()
