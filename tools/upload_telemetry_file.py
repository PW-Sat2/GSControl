import argparse
import os
import sys
from datetime import datetime, timedelta
from urlparse import urlparse

from influxdb import InfluxDBClient


sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'grafana_beacon_uploader'))

from summary import telemetry_file_mapper
from utils import ensure_byte_list
from data_point import generate_data_points

TELEMETRY_INTERVAL = timedelta(seconds=30)
MISSION_START = datetime(year=2018, month=12, day=3, hour=23, minute=10, second=00)

parser = argparse.ArgumentParser()

parser.add_argument('-d', '--influx', required=True,
                    help="InfluxDB url", default='http://localhost:8086/pwsat2')

parser.add_argument('-f', '--file', required=True,
                    help="Telemetry archive file (sorted by SEQ file)",
                    type=argparse.FileType('rb'))

parser.add_argument('-u', '--upload', required=False,
                    help="Store mapped telemetry items",
                    action='store_true')

parser.add_argument('--marker', required=False,
                    help="Session import marker")

parser.add_argument('--gs', required=True,
                    help="GS name")

args = parser.parse_args(sys.argv[1:])

raw = args.file.read()

raw = ensure_byte_list(raw)

entries = telemetry_file_mapper.read_telemetry_buffer(raw)

print 'Found {} entries in telemetry file'.format(len(entries))

url = urlparse(args.influx)
client = InfluxDBClient(host=url.hostname, port=url.port, database=url.path.strip('/'))

entry_mapping = telemetry_file_mapper.map_telemetry(client, entries)

for item in entry_mapping:
    print(item)

if not args.upload:
    print('NOT uploading')
    sys.exit(0)

tags = {
    'ground_station': args.gs
}

if args.marker:
    tags['import_marker'] = args.marker

all_points = []

for item in entry_mapping:
    item_points = generate_data_points(item.db_timestamp, item.telemetry_item, tags)
    all_points += item_points

print 'Total {} points'.format(len(all_points))

client.write_points(all_points)
