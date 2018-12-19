import os
import imp
import sys
import re
import argparse
from urlparse import urlparse
from datetime import datetime, timedelta
from glob import glob
from influxdb import InfluxDBClient
import shutil
import base64
from pprint import pprint

cfg_module = imp.new_module('config')
cfg_module.config = dict(
    VALID_CRC='0xBFFD'
)
sys.modules['config'] = cfg_module

sys.path.append(os.path.join(os.path.dirname(__file__), '../../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../grafana_beacon_uploader'))

from utils import ensure_byte_list
import response_frames
from radio.radio_frame_decoder import FallbackResponseDecorator
from devices import BeaconFrame
from data_point import generate_data_points
from tools.parse_beacon import ParseBeacon


gs_id_elka = 'e3fe087d-bf9c-4e4d-80c7-3366cfdec3e3'
gs_id_fp = '721762dd-8b8f-44b3-bfa7-66cfb12d39e1'

blacklist_user_id = ['f13d30a8-9bd2-4f26-93ad-32812d2e2443',]

class SMLFrame:
    def __init__(self, filename, data):
        regexp = re.match("(\d{8}-\d{6})-(.{36})-(.{36})\.bin", filename)

        self.date = datetime.strptime(regexp.group(1), '%Y%m%d-%H%M%S')
        self.user_id = regexp.group(2)
        self.frame_id = regexp.group(3)

        self.data = data[1:]

        if self.valid():
            frame_body = str(self.data[16:-2])

            frame_decoder = FallbackResponseDecorator(response_frames.FrameDecoder(response_frames.frame_factories))
            self.decoded_frame = frame_decoder.decode(ensure_byte_list(frame_body))

    def __repr__(self):
        return str(self.date) + " by " + self.user_id + ": " + base64.b64encode(self.data)

    def __hash__(self):
        return hash(str(self.date) + self.user_id + base64.b64encode(self.data))

    def __eq__(self, other):
        return self.date == other.date and \
               self.user_id == other.user_id and \
               self.data == other.data

    def __lt__(self, other):
        if self.date != other.date:
            return self.date < other.date

        # if one of ours - sort at the beginning
        if self.user_id == gs_id_elka:
            return False
        if self.user_id == gs_id_fp:
            return other.user_id == gs_id_elka

        if self.user_id != other.user_id:
            return self.user_id < other.user_id

        return self.data < other.data

    def valid(self):
        if self.data[0:16] != b'\xa0\xae\xa6\x82\xa8d\xe0\xa0\xae\xa6\x82\xa8da\x03\xf0':
            # print "Incorrect frame due to invalid callsign or AX25 header! ", self.frame_id
            return False

        return True

    def from_backlisted_user(self):
        if self.user_id in blacklist_user_id:
            # print "Frame from blacklisted user ", self.frame_id
            return True

        return False

    def __getitem__(self, item):
        return self.data[item]

    def data_b64(self):
        return base64.b64encode(self.data)

    def timestamp_string(self):
            return self.date.strftime("%Y-%m-%d_%H:%M:%S:%f")


def download_files(only_two_days=False):
    import urllib2
    from zipfile import ZipFile

    file_directory = os.path.dirname(os.path.abspath(__file__))
    bin_files_directory = os.path.join(file_directory, 'files')

    zip_file = os.path.join(bin_files_directory, 'files.zip')

    shutil.rmtree(bin_files_directory, ignore_errors=True)
    os.mkdir(bin_files_directory)

    url_with_bin_files = 'https://radio.pw-sat.pl/communication/log/export?f.tags=public&'
    if only_two_days:
        url_with_bin_files += 'f.from=' + (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        url_with_bin_files += 'f.from=2018-12-04'

    zip_file_bin = urllib2.urlopen(url_with_bin_files)
    with open(zip_file, 'wb') as output:
        output.write(zip_file_bin.read())

    zip = ZipFile(zip_file)
    frames = []
    filenames = zip.namelist()

    for filename in filenames:
        decoded_frame = zip.read(filename)
        decoded_frame = SMLFrame(os.path.basename(filename), bytearray(decoded_frame))
        if decoded_frame.valid() and not decoded_frame.from_backlisted_user():
            frames.append(decoded_frame)
    zip.close()
    shutil.rmtree(bin_files_directory, ignore_errors=True)

    # remove duplicate frames
    frames = sorted(list(set(frames)))

    return frames


def only_unique_packets(frames):
    return sorted(list({f.data_b64(): f for f in frames}.values()))


def filter_by_time(frames, timestamp, timespan_minutes=(-30, 10)):
    timestamp_begin = timestamp + timedelta(minutes=timespan_minutes[0])
    timestamp_end = timestamp + timedelta(minutes=timespan_minutes[1])

    filtered_frames = []
    for frame in frames:
        if timestamp_begin <= frame.date <= timestamp_end:
            filtered_frames.append(frame)
    return filtered_frames


def save_frames_to_csv(frames, filename):
    with open(filename, 'w') as file_output:
        for frame in frames:
            file_output.write(frame.timestamp_string() + ",D," + frame.data_b64() + "\n")


def merge_and_save_bin_beacons(frames, filename):
    with open(filename, 'wb') as r:
        for frame in frames:
            # extract only beacons
            if isinstance(frame.decoded_frame, response_frames.BeaconFrame):
                data = frame.data[16:-2]
                assert len(data) == 230
                r.write(data)


def send_beacons_to_grafana(frames):
    gs_grafana_name_elka = 'elka_gs_tmp'
    gs_grafana_name_fp = 'fp_gs_tmp'

    gs_grafana_name_others = 'radio_pwsat_pl'

    user_id_to_grafana = {
        gs_id_elka: gs_grafana_name_elka,
        gs_id_fp: gs_grafana_name_fp
    }

    def get_grafana_gs_name(frame):
        return user_id_to_grafana.get(frame.user_id, gs_grafana_name_others)

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--influx', required=False, help="InfluxDB url",
                        default="http://grafana.pw-sat.pl:8086/pwsat2")
    args = parser.parse_args(sys.argv[1:])
    url = urlparse(args.influx)
    db = InfluxDBClient(host=url.hostname, port=url.port, database=url.path.strip('/'))

    db.delete_series(tags={'ground_station': 'radio_pwsat_pl'})

    for frame in frames:
        frame_body = str(frame.data[16:-2])

        frame_decoder = FallbackResponseDecorator(
            response_frames.FrameDecoder(response_frames.frame_factories))
        decoded_frame = frame_decoder.decode(ensure_byte_list(frame_body))

        if isinstance(decoded_frame, BeaconFrame):
            telemetry = ParseBeacon.parse(decoded_frame)
            print(telemetry)

            points = generate_data_points(frame.date, telemetry, {
                'ground_station': get_grafana_gs_name(frame)
            })

            db.write_points(points)


def get_elka_frames(frames):
    return filter(lambda f: f.user_id == gs_id_elka, frames)


def get_fp_frames(frames):
    return filter(lambda f: f.user_id == gs_id_fp, frames)


def get_ham_frames(frames):
    return filter(lambda f: f.user_id != gs_id_fp and f.user_id != gs_id_elka, frames)
