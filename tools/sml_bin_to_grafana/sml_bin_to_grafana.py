import os
import sys
import argparse
from urlparse import urlparse
from datetime import datetime
from glob import glob
from influxdb import InfluxDBClient
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), '../../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../grafana_beacon_uploader'))

from utils import ensure_byte_list
import response_frames
from radio.radio_frame_decoder import FallbackResponseDecorator
from devices import BeaconFrame
from data_point import generate_data_points
from tools.parse_beacon import ParseBeacon



file_directory = os.path.dirname(os.path.abspath(__file__))
bin_files_directory = os.path.join(file_directory, 'files')


def download_files():
    import urllib2
    from zipfile import ZipFile

    zip_file = os.path.join(bin_files_directory, 'files.zip')

    shutil.rmtree(bin_files_directory, ignore_errors=True)
    os.mkdir(bin_files_directory)

    url_with_bin_files = 'https://radio.pw-sat.pl/communication/log/export?f.from=2018-12-04&f.tags=telemetry'

    zip_file_bin = urllib2.urlopen(url_with_bin_files)
    with open(zip_file, 'wb') as output:
        output.write(zip_file_bin.read())

    zip = ZipFile(zip_file)
    zip.extractall(bin_files_directory)


download_files()

all_frames = []

files_glob = glob(os.path.join(bin_files_directory, '*.bin'))

for filename in files_glob:
    with open(filename, 'rb') as frame:
        x = bytearray(frame.read())
        all_frames.append([os.path.basename(filename), x])

# remove all files
shutil.rmtree(bin_files_directory, ignore_errors=True)

# sort frames by time received
all_frames = sorted(all_frames)

def remove_duplicate_frames(all_frames):
    already = []
    all_frames_filtered = []
    for i in all_frames:
        if i[1] not in already:
            already.append(i[1])
            all_frames_filtered.append(i)
    return all_frames_filtered


all_frames_removed = remove_duplicate_frames(all_frames)
print "All frames:", len(all_frames)
print "Unique frames:", len(all_frames_removed)
all_frames = all_frames_removed

all_frames = sorted(all_frames)


def filter_frames(all_frames):
    for i in all_frames:
        data = i[1]

        # first byte is hard-coded of AX25 frame header 0x7E
        if data[0:17] != b'\x7e\xa0\xae\xa6\x82\xa8d\xe0\xa0\xae\xa6\x82\xa8da\x03\xf0':
            print "Incorrect frame due to invalid callsign or AX25 header!"
            continue

        if data[17] != 0xCD:
            print "Not beacon!", data[17]
            continue

        yield i


all_frames = list(filter_frames(all_frames))

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--influx', required=True, help="InfluxDB url")
args = parser.parse_args(sys.argv[1:])
url = urlparse(args.influx)
db = InfluxDBClient(host=url.hostname, port=url.port, database=url.path.strip('/'))

db.delete_series(tags={'ground_station': 'radio_pwsat_pl'})

for i in all_frames:
    name = i[0]
    frame_body = i[1][17:-2]
    frame_body = str(frame_body)

    frame_decoder = FallbackResponseDecorator(response_frames.FrameDecoder(response_frames.frame_factories))
    frame = frame_decoder.decode(ensure_byte_list(frame_body))

    if not isinstance(frame, BeaconFrame):
        print(type(frame))
        continue

    telemetry = ParseBeacon.parse(frame)
    print(telemetry)

    date = '-'.join(name.split('-')[0:2])
    timestamp = datetime.strptime(date, '%Y%m%d-%H%M%S')

    print(timestamp)

    points = generate_data_points(timestamp, telemetry, {
        'ground_station': 'radio_pwsat_pl'
    })

    db.write_points(points)
