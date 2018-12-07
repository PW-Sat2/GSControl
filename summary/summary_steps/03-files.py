from collections import defaultdict
from pprint import pformat

from typing import List

import telecommand as tcs


def list_requested_files(session):
    download_files = []  # type: List[tcs.DownloadFile]

    for [cmd, _, _] in session.tasklist:
        raw_cmd = cmd

        if isinstance(cmd, list):
            raw_cmd = cmd[0]

        if isinstance(raw_cmd, tcs.DownloadFile):
            download_files.append(raw_cmd)

    files = defaultdict(set)

    for cmd in download_files:
        files[cmd._path].update(cmd._seqs)

    for file in files.keys():
        files[file] = list(files[file])

    text = pformat(dict(files))
    session.write_artifact('requested_files.txt', text)
