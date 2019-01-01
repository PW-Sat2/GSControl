import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append( os.path.join(os.path.dirname(__file__), '..'))

# TODO: GS array
# TODO: Receiver thread per step
# TODO: Some context to hold all received/uplinked frames
# TODO: Load config
# TODO: Connect all receivers

def run():
    session_file = os.path.join(os.path.dirname(__file__), 'keep_alive.py')

    scope = {}

    with open(session_file, 'r') as f:
        exec(f, scope)

    session = scope['session']

    steps = list(session())

    for step in steps:
        step()


run()
