import struct
from math import ceil

from response_frames.file_system import FileListSuccessFrame

from bench_init import *


def parse_file_list(frame):
    if isinstance(frame, FileListSuccessFrame):
        res = bytearray(frame.payload())[2:]

        file_list = []

        while True:
            now = res.find('\x00')
            if now == -1:
                return file_list

            name = str(res[:now])
            size = struct.unpack('<I', res[now + 1:now + 5])[0]
            chunks = int(ceil(size / 230.))

            file_list.append({'File': name, 'Size': size, 'Chunks': chunks})
            res = res[now + 5:]
    else:
        file_list = None

    return file_list


def list_files():
    frames = send(tc.fs.ListFiles("/"))
    files = []
    for f in frames:
        files.extend(parse_file_list(f))
    PrintLog(str(files))
    return files


def get_file_info(filename):
    file_list = list_files()
    for f in file_list:
        if f["File"] == filename:
            PrintLog("File {} info: {}".format(filename, f))
            return f
    PrintLog("File {} not found".format(filename))
    return None
