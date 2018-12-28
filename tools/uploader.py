import base64
import datetime
import requests
import json
import progressbar
import urllib3
from datetime import timedelta
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = 'https://radio.pw-sat.pl'
TZ_OFFSET = timedelta(seconds=time.timezone)

def load_frames(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            (ts, direction, frame_content) = line.split(',')

            if direction != 'D':
                continue

            ts = datetime.datetime.strptime(ts, "%Y-%m-%d_%H:%M:%S:%f")
            yield ts, frame_content


def create_session(credentials_file):
    s = requests.Session()

    s.verify = False

    s.headers = {
        'content-type': 'application/json'
    }

    with open(credentials_file, 'r') as f:
        credentials = json.load(f)

    resp = s.post(url=BASE_URL + '/api/authenticate',
                  json=credentials)

    return s


def put_frame(session, (ts, frame_content)):
    local_ts = ts - TZ_OFFSET
    data = {
        'frame': frame_content,
        'timestamp': int(time.mktime(local_ts.timetuple())) * 1000,
        'traffic': 'Rx'
    }

    r = session.put(BASE_URL + '/communication/frame', json=data)


def main(credentials_file, frames_file):
    frames = list(load_frames(frames_file))

    session = create_session(credentials_file)

    for frame in progressbar.progressbar(frames):
        put_frame(session, frame)


import sys

main(sys.argv[1], sys.argv[2])
