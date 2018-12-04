import base64
import sys

import argparse
from datetime import datetime
from urlparse import urlparse

import colorlog
import os
import logging

from influxdb import InfluxDBClient

sys.path.append(os.path.join(os.path.dirname(__file__), '../../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils import ensure_byte_list
import response_frames
from radio.radio_frame_decoder import FallbackResponseDecorator
from devices import BeaconFrame
from data_point import generate_data_points
from tools.parse_beacon import ParseBeacon


if os.getenv("CLICOLOR_FORCE") == "1":
    print "Forcing colors"
    import colorama

    colorama.deinit()


def _setup_log():
    root_logger = logging.getLogger()

    handler = colorlog.StreamHandler()

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)-15s %(levelname)s: [%(name)s] %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


_setup_log()

parser = argparse.ArgumentParser()
parser.add_argument("--gs", type=str, help="GS name", required=True)
parser.add_argument("--file", type=argparse.FileType('r'), help="File in downlink_frames file format", required=True)
parser.add_argument('-d', '--influx', required=True, help="InfluxDB url")
args = parser.parse_args(sys.argv[1:])

LOG = logging.getLogger("main")
LOG.info("Reading frames from {}".format(args.file.name))

url = urlparse(args.influx)
db = InfluxDBClient(host=url.hostname, port=url.port, database=url.path.strip('/'))

for l in args.file.readlines():
    (timestamp, direction, payload) = l.split(',')

    if direction != 'D':
        continue

    timestamp = datetime.strptime(timestamp, '%Y-%m-%d_%H:%M:%S:%f')
    payload = base64.b64decode(payload)
    frame_body = payload[16:-2]

    frame_body = ensure_byte_list(frame_body)

    frame_decoder = FallbackResponseDecorator(response_frames.FrameDecoder(response_frames.frame_factories))
    frame = frame_decoder.decode(frame_body)
    if not isinstance(frame, BeaconFrame):
        continue

    telemetry = ParseBeacon.parse(frame)

    points = generate_data_points(timestamp, telemetry, {
        'ground_station': args.gs
    })

    db.write_points(points)