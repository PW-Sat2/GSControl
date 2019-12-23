import logging
from os import path
from os import SEEK_SET
from summary.scope import session
from tools.remote_files import RemoteFileTools
from utils import ensure_byte_list


def decode_photo(file_name, output_file_name=None):
    chunks = []

    (basename, _) = path.splitext(file_name)
    jpg_file_name = output_file_name or (basename + '.jpg')

    with session.open_artifact(file_name, 'rb') as raw_file:
        with open(session.expand_artifact_path(jpg_file_name), 'wb') as jpg_file:
            raw_file.seek(4, SEEK_SET)
            
            while True:
                chunk = raw_file.read(512)
                if chunk == '':
                    break

                jpg_file.write(chunk[0:512 - 6])