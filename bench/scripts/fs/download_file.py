from utils import ensure_string

from tools.photo import parse_photo

from bench_init import *


def download_file(obc_filename, ground_filename=None, max_chunks_at_once=20):
    if ground_filename is None:
        ground_filename = obc_filename

    file_info = scripts.fs.get_file_info(obc_filename)

    if file_info is None:
        PrintLog("File {} does not exist! Cannot download.".format(obc_filename))
        return

    chunks = file_info["Chunks"]

    file_chunks = [x for x in range(0, chunks)]
    remaining = [x for x in range(0, chunks)]

    while len(remaining) > 0:
        if max_chunks_at_once > len(remaining):
            request_qty = len(remaining)
        else:
            request_qty = max_chunks_at_once

        chunks_request_now = [remaining[i] for i in range(request_qty)]
        collected_frames = send(tc.fs.DownloadFile(obc_filename, chunks_request_now))
        # check_equal('Collected frames', len(collected_frames), request_qty)

        for frame in collected_frames:
            file_chunks[frame.seq()] = frame.response
            remaining.remove(frame.seq())
            PrintLog("Got {}/{}".format(frame.seq() + 1, chunks))

    from config import config

    data_string = ""
    for i in file_chunks:
        data_string += ensure_string(i)

    with open(os.path.join(config['output_path'], config['test_name'], ground_filename), 'wb') as f:
        f.write(data_string)
        PrintLog("Saved file {} to {}".format(obc_filename, ground_filename))


def download_photo(obc_filename, ground_filename=None, max_chunks_at_once=20):
    if ground_filename is None:
        ground_filename = obc_filename

    download_file(obc_filename, ground_filename, max_chunks_at_once)
    parse_photo(ground_filename)
