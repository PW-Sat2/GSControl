import logging
from os import path
from pprint import pformat

from summary.scope import session, store
from summary.steps_lib.files import get_requested_files, get_downloaded_files
from summary.steps_lib.frame_utils import unique_seqs
from tools.remote_files import RemoteFileTools
from utils import ensure_string


def write_file_from_description(file_path, description):
    missing_chunk_ids = description['MissingChunks']
    error_chunk_ids = description['ErrorChunks']
    downloaded_chunks = description['ChunkFrames']

    missing_file_name = file_path + '.missing'

    if len(missing_chunk_ids) > 0:
        session.write_artifact(missing_file_name, ', '.join(map(str, missing_chunk_ids)))
    else:
        if session.has_artifact(missing_file_name):
            logging.warning('Removing obsolete missing file {}'.format(missing_file_name))
            session.remove_artifact(missing_file_name)

    if len(error_chunk_ids) > 0:
        session.write_artifact(file_path + '.error', ', '.join(map(str, error_chunk_ids)))

    (base_name, ext) = path.splitext(file_path)

    is_jpg = ext == '.jpg'

    if is_jpg:
        jpg_file_name = base_name + '.jpg'
        file_path = base_name + '.raw'
    else:
        jpg_file_name = None

    with session.open_artifact(file_path, 'wb') as f:
        for chunk in downloaded_chunks:
            f.write(ensure_string(chunk.response))

    if is_jpg:
        just_responses = []

        for f in description['ChunkFrames']:
            just_responses.append(f.response)

        RemoteFileTools.save_photo(session.expand_artifact_path(jpg_file_name), just_responses)


def list_requested_files():
    files = get_requested_files(session.tasklist)

    text = pformat(files)
    session.write_artifact('requested_files.txt', text)


def extract_downloaded_files():
    files = get_downloaded_files(session.tasklist, session.all_frames)

    for file_name in files.keys():
        logging.info(
            'Saving extracted file (this session) {} ({} chunks requested, {} downloaded, {} missing, {} errors)'.format(
                file_name,
                len(files[file_name]['RequestedChunks']),
                len(files[file_name]['DownloadedChunks']),
                len(files[file_name]['MissingChunks']),
                len(files[file_name]['ErrorChunks'])
            ))
        write_file_from_description(file_name, files[file_name])


def extract_file(file_name, also=[]):
    sessions = [session]

    for id in also:
        sessions.append(store.get_session(id))

    file_frames = []
    requested_chunks = set()
    error_chunk_ids = set()

    for s in sessions:
        session_frames = s.all_frames

        files = get_downloaded_files(s.tasklist, session_frames)

        if file_name in files:
            file = files[file_name]

            file_frames.extend(file['ChunkFrames'])
            requested_chunks.update(file['RequestedChunks'])
            error_chunk_ids.update(file['ErrorChunks'])
        else:
            logging.warning('File {} not found in session {}'.format(file_name, s.session_number))

    file_frames = unique_seqs(file_frames)
    file_frames = sorted(file_frames, key=lambda f: f.seq())

    dowloaded_chunk_ids = map(lambda f: f.seq(), file_frames)

    file = {
        'MissingChunks': list(set(requested_chunks).difference(dowloaded_chunk_ids).difference(error_chunk_ids)),
        'ChunkFrames': file_frames,
        'RequestedChunks': requested_chunks,
        'DownloadedChunks': dowloaded_chunk_ids,
        'ErrorChunks': list(set(error_chunk_ids).difference(dowloaded_chunk_ids))
    }

    session_ids = sorted(map(lambda s: str(s.session_number), sessions))

    logging.info(
        'Saving extracted file {} (sessions: {}) ({} chunks requested, {} downloaded, {} missing, {} errors)'.format(
            file_name,
            ', '.join(session_ids),
            len(file['RequestedChunks']),
            len(file['DownloadedChunks']),
            len(file['MissingChunks']),
            len(file['ErrorChunks'])
        ))

    write_file_from_description(path.join('assembled', file_name.strip('/')), file)
