import logging
from os import path
from summary.scope import session
from tools.remote_files import RemoteFileTools
from utils import ensure_byte_list


def decode_photo(file_name, output_file_name=None):
    chunks = []

    with session.open_artifact(file_name, 'rb') as f:
        while True:
            chunk = f.read(230)
            if chunk == '':
                break

            chunks.append(ensure_byte_list(chunk))

    logging.info('Decoding photo {} ({} chunks)'.format(file_name, len(chunks)))

    (basename, _) = path.splitext(file_name)
    jpg_file_name = output_file_name or (basename + '.jpg')

    RemoteFileTools.save_photo(session.expand_artifact_path(jpg_file_name), chunks)
