import zmq
import sys
import os
from typing import List, Union

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from radio.radio_receiver import Receiver
from radio.radio_sender import Sender
import telecommand as tc
import response_frames as rf
from utils import ensure_byte_list


Decoder = rf.FrameDecoder(rf.frame_factories)

GS_LIST = [
    ('flatsat', 7001, 7000)
]

CHUNKS_PER_TC = 20


class GroundStation(object):
    def __init__(self, host_name, downlink_port, uplink_port):
        self.host_name = host_name
        self.receiver = Receiver(target=host_name, port=downlink_port)
        self.sender = Sender(target=host_name, port=uplink_port, source_callsign='SP9NOV')

    def __repr__(self):
        return 'GS: {}'.format(self.host_name)


def receive_file_parts(stations, correlation_id, requested_chunks):
    # type: (List[GroundStation], int, List[int]) -> List[Union[rf.FileSendSuccessFrame, rf.FileSendErrorFrame]]

    socks = map(lambda s: s.receiver.sock, stations)
    result = []

    timeout_secs = 10

    remaining_chunks = list(requested_chunks)

    while True:
        (r, _, _) = zmq.select(socks, [], [], timeout=timeout_secs)

        timeout_secs = 5

        if not r:
            break

        for socket in r:
            frame_raw = socket.recv()
            frame_raw = frame_raw[16:-2]
            frame_raw = ensure_byte_list(frame_raw)
            frame = Decoder.decode(frame_raw)

            print '\tReceived {} (Remaining: {})'.format(repr(frame), remaining_chunks)

            if (isinstance(frame, rf.FileSendSuccessFrame) or isinstance(frame, rf.FileSendErrorFrame)) and frame.correlation_id == correlation_id:
                result.append(frame)

                if frame.seq() in remaining_chunks:
                    idx = remaining_chunks.index(frame.seq())
                    remaining_chunks = remaining_chunks[idx + 1:]

        if not remaining_chunks:
            break

    return result


def download_chunks(uplink_station, all_stations, file_name, correlation_id, chunks):
    cmd = tc.DownloadFile(correlation_id=correlation_id, path=file_name, seqs=chunks)

    downloaded = []
    attempt = 0

    while not downloaded:
        if attempt >= 10:
            break

        attempt += 1

        print 'Download chunks {}. Attempt: {}. TC: {}'.format(chunks, attempt, cmd)
        uplink_station.sender.send(cmd.frame())
        downloaded = receive_file_parts(all_stations, correlation_id, chunks)

    return downloaded


def run():
    correlation_id = 123
    file = '/telemetry.previous'
    chunks = range(0, 2280, 10)

    stations = map(lambda args: GroundStation(*args), GS_LIST)

    remaining_chunks = list(chunks)

    while True:
        if not remaining_chunks:
            print 'Everything downloaded'
            break

        uplink_station = stations[0]

        download_part = remaining_chunks[0:CHUNKS_PER_TC]

        print 'Downloading chunks {} ({} of {} in remaining)'.format(download_part, len(download_part), len(remaining_chunks))

        downloaded = download_chunks(uplink_station, stations, file, correlation_id, download_part)

        seqs = map(lambda f: f.seq(), downloaded)

        print 'Actually downloaded {} of {} requested ({})'.format(len(downloaded), len(download_part), seqs)

        for f in downloaded:
            print '\tProcessing {}'.format(repr(f))
            if f.seq() in remaining_chunks:
                remaining_chunks.remove(f.seq())


import imp
imp.load_source('config', 'C:/PW-Sat/obc-build/integration_tests/config.py')

run()
