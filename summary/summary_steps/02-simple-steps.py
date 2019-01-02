import logging
from collections import defaultdict
from pprint import pformat, pprint

import response_frames
from tools.remote_files import RemoteFileTools
from summary.scope import session
from summary.steps_lib.frame_utils import only_type


def save_file_lists():
    list_files = only_type(session.all_frames, response_frames.FileListSuccessFrame)
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

        logging.info('Saving file list with correlation id={}'.format(cid))
        session.write_artifact('file_list_{}.txt'.format(cid), text)


def save_beacons():
    beacons = only_type(session.all_frames, response_frames.BeaconFrame)

    texts = []

    for beacon in beacons:
        texts.append(str(beacon))

    logging.info('Saving {} beacons (short form)'.format(len(beacons)))
    session.write_artifact('beacons.txt', '\n\n'.join(texts))


def save_frames_list():
    with session.open_artifact('downlink_frames.txt', 'w') as f:
        for frame in session.all_frames:
            pprint(frame, f)
