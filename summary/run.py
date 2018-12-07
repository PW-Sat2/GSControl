import sys
import os
import imp
from collections import defaultdict
from pprint import pprint, pformat

cfg_module = imp.new_module('config')
cfg_module.config = dict(
    VALID_CRC='0xBFFD'
)
sys.modules['config'] = cfg_module

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mission_store import MissionStore
import response_frames
from tools.remote_files import RemoteFileTools


def only_type(frames, frame_type):
    return filter(lambda f: isinstance(f, frame_type), frames)


def save_file_lists(session, frames):
    list_files = only_type(frames, response_frames.FileListSuccessFrame)
    by_cid = defaultdict(list)

    for frame in list_files:
        by_cid[frame.correlation_id].append(frame)

    for cid in sorted(by_cid.keys()):
        parts = sorted(by_cid[cid], key=lambda f: f.seq())

        files = []

        for part in parts:
            files.extend(RemoteFileTools.parse_file_list(part))

        files = sorted(files, key=lambda f: f['File'])
        text = pformat(files)

        session.write_artifact('file_list_{}.txt'.format(cid), text)


def save_beacons(session, frames):
    beacons = only_type(frames, response_frames.BeaconFrame)

    texts = []

    for beacon in beacons:
        texts.append(str(beacon))

    session.write_artifact('beacons.txt', '\n\n'.join(texts))


def run_summary(store, current_session):
    session = store.get_session(current_session)

    frames = session.frames(['elka', 'gliwice'])

    save_file_lists(session, frames)
    save_beacons(session, frames)


def main():
    mission_data = os.path.abspath('../mission')
    store = MissionStore(root=mission_data)
    session = 16
    run_summary(store, session)


main()
