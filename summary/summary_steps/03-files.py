from collections import defaultdict
from pprint import pformat

from typing import List

import response_frames
import telecommand as tcs
from utils import ensure_string


def get_requested_files(tasklist):
    download_files = []  # type: List[tcs.DownloadFile]

    for [cmd, _, _] in tasklist:
        raw_cmd = cmd

        if isinstance(cmd, list):
            raw_cmd = cmd[0]

        if isinstance(raw_cmd, tcs.DownloadFile):
            download_files.append(raw_cmd)

    files = defaultdict(lambda: {'CorrelationIds': set(), 'Chunks': set()})

    for cmd in download_files:
        files[cmd._path.lstrip('/')]['Chunks'].update(cmd._seqs)
        files[cmd._path.lstrip('/')]['CorrelationIds'].add(cmd.correlation_id())

    simple_files = {}

    for file in files.keys():
        simple_files[file] = {
            'CorrelationIds': list(files[file]['CorrelationIds']),
            'Chunks': list(files[file]['Chunks'])
        }

    return simple_files


def list_requested_files(session):
    files = get_requested_files(session.tasklist)

    text = pformat(files)
    session.write_artifact('requested_files.txt', text)


def extract_downloaded_files(session, frames):
    files = get_requested_files(session.tasklist)

    file_chunks = only_type(frames, response_frames.FileSendSuccessFrame)

    for file_name in files.keys():
        requested_chunk_ids = files[file_name]['Chunks']
        correlation_ids = files[file_name]['CorrelationIds']

        downloaded_chunks = filter(lambda f: f.correlation_id in correlation_ids, file_chunks)
        downloaded_chunks = sorted(downloaded_chunks, key=lambda f: f.seq())
        downloaded_chunks = unique_seqs(downloaded_chunks)

        downloaded_chunk_ids = map(lambda f: f.seq(), downloaded_chunks)

        missing_chunk_ids = set(requested_chunk_ids).difference(downloaded_chunk_ids)

        if len(missing_chunk_ids) > 0:
            session.write_artifact(file_name + '.missing', ', '.join(map(str, missing_chunk_ids)))

        with session.open_artifact(file_name, 'wb') as f:
            for chunk in downloaded_chunks:
                f.write(ensure_string(chunk.response))
