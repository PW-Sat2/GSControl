from collections import defaultdict
from pprint import pformat

import response_frames
from tools.remote_files import RemoteFileTools


def only_type(frames, frame_type):
    return filter(lambda f: isinstance(f, frame_type), frames)


def unique_seqs(frames):
    result = []
    seqs = set()

    for frame in frames:
        if frame.seq() in seqs:
            continue

        result.append(frame)
        seqs.add(frame.seq())

    return result


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

