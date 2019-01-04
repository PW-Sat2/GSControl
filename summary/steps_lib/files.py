from collections import defaultdict

import response_frames
import telecommand as tcs
from typing import List

from summary.steps_lib.frame_utils import only_type, unique_seqs


def get_requested_files(tasklist):
    download_files = []  # type: List[tcs.DownloadFile]

    for [cmd, _, _] in tasklist:
        raw_cmd = cmd

        if isinstance(cmd, list):
            raw_cmd = cmd[0]

        if isinstance(raw_cmd, tcs.DownloadFile):
            download_files.append(raw_cmd)

    files = defaultdict(lambda: {'CorrelationIds': set(), 'RequestedChunks': set()})

    for cmd in download_files:
        files[cmd._path.lstrip('/')]['RequestedChunks'].update(cmd._seqs)
        files[cmd._path.lstrip('/')]['CorrelationIds'].add(cmd.correlation_id())

    simple_files = {}

    for file in files.keys():
        simple_files[file] = {
            'CorrelationIds': list(files[file]['CorrelationIds']),
            'RequestedChunks': list(files[file]['RequestedChunks'])
        }

    return simple_files


def get_downloaded_files(tasklist, frames):
    files = dict(get_requested_files(tasklist))

    file_chunks = only_type(frames, response_frames.FileSendSuccessFrame)
    error_frames = only_type(frames, response_frames.FileSendErrorFrame)

    for file_name in files.keys():
        requested_chunk_ids = files[file_name]['RequestedChunks']
        correlation_ids = files[file_name]['CorrelationIds']

        downloaded_chunks = filter(lambda f: f.correlation_id in correlation_ids, file_chunks)
        downloaded_chunks = unique_seqs(downloaded_chunks)
        downloaded_chunks = sorted(downloaded_chunks, key=lambda f: f.seq())

        error_chunks = filter(lambda f: f.correlation_id in correlation_ids, error_frames)
        error_chunks = unique_seqs(error_chunks)
        error_chunks = sorted(error_chunks, key=lambda f: f.seq())
        error_chunk_ids = map(lambda f: f.seq(), error_chunks)

        downloaded_chunk_ids = map(lambda f: f.seq(), downloaded_chunks)

        missing_chunk_ids = set(requested_chunk_ids).difference(downloaded_chunk_ids).difference(error_chunk_ids)

        files[file_name]['DownloadedChunks'] = downloaded_chunk_ids
        files[file_name]['MissingChunks'] = sorted(list(missing_chunk_ids))
        files[file_name]['ChunkFrames'] = downloaded_chunks
        files[file_name]['ErrorChunks'] = error_chunk_ids

    return files
