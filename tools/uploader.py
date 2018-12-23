import base64
import datetime
import time

# print 'aa'
#
# with open("C:/Users/Novakov/Downloads/b50c5a39-12a9-40ce-9e5c-cdaffe512cc0.bin", 'rb') as f:
#     text = f.read()
#
# with open('D:/tmp/test.frames', 'w') as f:
#     for i in range(0, 200):
#         f.write('2018-09-11_10:49:16:803446,D,{}\n'.format(base64.b64encode(text[1:])))

import requests
import json
import progressbar
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = 'https://radio.pw-sat.pl'


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
    s.proxies = {
      'http': 'http://127.0.0.1:8888',
      'https': 'http://127.0.0.1:8888',
    }
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
    data = {
        'frame': frame_content,
        'timestamp': int(time.mktime(ts.timetuple())) * 1000,
        'traffic': 'Rx'
    }

    session.put(BASE_URL + '/communication/frame', json=data)


def main(credentials_file, frames_file):
    frames = list(load_frames(frames_file))

    session = create_session(credentials_file)

    for frame in progressbar.progressbar(frames):
        put_frame(session, frame)


import sys

main(sys.argv[1], sys.argv[2])
