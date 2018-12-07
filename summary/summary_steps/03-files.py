from collections import defaultdict
from os import path
from pprint import pformat

from typing import List

import response_frames
import telecommand as tcs
from tools.remote_files import RemoteFileTools
from utils import ensure_string


def write_file_from_description(session, file_path, description):
    missing_chunk_ids = description['MissingChunks']
    downloaded_chunks = description['ChunkFrames']

    if len(missing_chunk_ids) > 0:
        session.write_artifact(file_path + '.missing', ', '.join(map(str, missing_chunk_ids)))

    (base_name, ext) = path.splitext(file_path)

    is_jpg = ext == '.jpg'

    if is_jpg:
        jpg_file_name = base_name + '.jpg'
        file_path = base_name + '.raw'

    with session.open_artifact(file_path, 'wb') as f:
        for chunk in downloaded_chunks:
            f.write(ensure_string(chunk.response))

    if is_jpg:
        just_responses = []

        for f in description['ChunkFrames']:
            just_responses.append(f.response)

        RemoteFileTools.save_photo(session.expand_artifact_path(jpg_file_name), just_responses)


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


def list_requested_files(session):
    files = get_requested_files(session.tasklist)

    text = pformat(files)
    session.write_artifact('requested_files.txt', text)


def get_downloaded_files(tasklist, frames):
    files = dict(get_requested_files(tasklist))

    file_chunks = only_type(frames, response_frames.FileSendSuccessFrame)

    for file_name in files.keys():
        requested_chunk_ids = files[file_name]['RequestedChunks']
        correlation_ids = files[file_name]['CorrelationIds']

        downloaded_chunks = filter(lambda f: f.correlation_id in correlation_ids, file_chunks)
        downloaded_chunks = unique_seqs(downloaded_chunks)
        downloaded_chunks = sorted(downloaded_chunks, key=lambda f: f.seq())

        downloaded_chunk_ids = map(lambda f: f.seq(), downloaded_chunks)

        missing_chunk_ids = set(requested_chunk_ids).difference(downloaded_chunk_ids)

        files[file_name]['DownloadedChunks'] = downloaded_chunk_ids
        files[file_name]['MissingChunks'] = list(missing_chunk_ids)
        files[file_name]['ChunkFrames'] = downloaded_chunks

    return files


def extract_downloaded_files(session, frames):
    files = get_downloaded_files(session.tasklist, frames)

    for file_name in files.keys():
        write_file_from_description(session, file_name, files[file_name])


def extract_file(current_session, file_name, also=[]):
    sessions = [current_session]

    for id in also:
        sessions.append(store.get_session(id))

    file_frames = []
    requested_chunks = []

    for session in sessions:
        session_frames = session.frames(['all'])

        files = get_downloaded_files(session.tasklist, session_frames)

        file = files[file_name]

        file_frames.extend(file['ChunkFrames'])
        requested_chunks.extend(file['RequestedChunks'])


    file_frames = unique_seqs(file_frames)
    file_frames = sorted(file_frames, key=lambda f: f.seq())

    dowloaded_chunk_ids = map(lambda f: f.seq(), file_frames)

    file = {
        'MissingChunks': list(set(requested_chunks).difference(dowloaded_chunk_ids)),
        'ChunkFrames': file_frames
    }

    write_file_from_description(session, path.join('assembled', file_name.strip('/')), file)
