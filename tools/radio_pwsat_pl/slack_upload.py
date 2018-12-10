import requests
import time
import fuckit
import argparse
from pprint import pformat
from radio_pwsat_pl_common import *


parser = argparse.ArgumentParser()

parser.add_argument('-u', '--url', required=True,
                help="Slack URL to upload")
args = parser.parse_args()

slack_url = args.url

def get_frames():
    all_frames = download_files()

    # leave only unique data frames
    all_frames = sorted(list({f.data_b64(): f for f in all_frames}.values()))

    return all_frames


frames_now = get_frames()
# print frames_now

while True:
    with fuckit:
        frames = get_frames()

        new_frames = list(set(frames) - set(frames_now))
        frames_now = frames

        for i in new_frames:
            # drop test frames
            if isinstance(i.decoded_frame, response_frames.PeriodicMessageFrame) and \
               i.data.find("ABCDEFGHIJKLMNOPQRSTUVWXYZ") != -1:
                continue

            date = i.date.strftime("%Y-%m-%d %H:%M:%S: ")

            if isinstance(i.decoded_frame, response_frames.BeaconFrame):
                date += str(i.decoded_frame._parsed['03: Time Telemetry']['0072: Mission time'])[:-7] + ": "

            x = pformat(i.decoded_frame)
            print(date + x)

            r = requests.post(slack_url,
                              json={'text': date + x})

        time.sleep(1)
