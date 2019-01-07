import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from radio import analyzer
import telecommand as tc
import matplotlib.pyplot as plt


def run(session_id):
    tasklist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'mission', 'sessions', session_id, 'tasklist.py'))
    print('Loading tasklist from {}'.format(tasklist_path))
    tasklist = analyzer.Analyzer().load(tasklist_path)

    file_chunks = {
        'telemetry.current': set(),
        'telemetry.previous': set()
    }

    for [cmd, _, _] in tasklist:
        if not isinstance(cmd, tc.DownloadFile):
            continue

        if cmd._path.lstrip('/') in file_chunks:
            file_chunks[cmd._path.lstrip('/')].update(cmd._seqs)

    total_chunks = len(file_chunks['telemetry.current']) + len(file_chunks['telemetry.previous'])

    import numpy as np

    x = np.arange(0, total_chunks, 1)
    y = list(file_chunks['telemetry.current']) + map(lambda c: -(2280 - c - 1), file_chunks['telemetry.previous'])
    y = sorted(y)

    deltas = []
    prev = y[0]
    for c in y[1:]:
        deltas.append(c - prev)
        prev = c

    fig, ax = plt.subplots(2, 1)

    ax[0].scatter(x[1:], deltas)
    ax[1].hist(deltas)

    plt.show()


run(sys.argv[1])
