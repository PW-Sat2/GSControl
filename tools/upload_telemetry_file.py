import argparse
from urlparse import urlparse

from bitarray import bitarray
from datetime import datetime, timedelta
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet
from struct import pack
import progressbar
import dateutil.parser
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'grafana_beacon_uploader'))

from utils import ensure_byte_list
from emulator.beacon_parser.full_beacon_parser import FullBeaconParser
from emulator.beacon_parser.parser import BitReader, BeaconStorage
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

entries = []

with progressbar.ProgressBar(max_value=len(raw)) as bar:
    while len(raw) >= 230:
        if raw[0] == 0xCD:
            raw = raw[1:]

        part = raw[0:230]
        raw = raw[230:]
        try:
            all_bits = bitarray(endian='little')
            all_bits.frombytes(''.join(map(lambda x: pack('B', x), part)))

            reader = BitReader(all_bits)
            store = BeaconStorage()

            parsers = FullBeaconParser().GetParsers(reader, store)
            parsers.reverse()

            while len(parsers) > 0:
                parser = parsers.pop()
                parser.parse()

            entries.append(store.storage)
        except:
            pass

        bar.update(bar.value + 230)

print 'Found {} entries in telemetry file'.format(len(entries))

client = InfluxDBClient(database='pwsat2', host='grafana.pw-sat.pl')

search_query_next_match = '''
select 
    "Time Telemetry.Mission time", "Time Telemetry.External time" 
from beacon 
where 
    "Time Telemetry.Mission time" >= {mission_time}
and 
    "Time Telemetry.External time" >= {external_time}
and ground_station <> 'telemetry-archive'
and time > '2018-12-04 23:10:00'
order by time
limit 1
'''

found = 0
not_found = 0
inconclusive = 0

bar = progressbar.ProgressBar(max_value=len(entries))

entry_mapping = []


class EntryMapping(object):
    def __init__(self, telemetry_item):
        self.db_timestamp = None
        self.interpolated_timestamp = None
        self.telemetry_item = telemetry_item

    def match_to(self, db_timestamp):
        self.db_timestamp = db_timestamp

    def mission_time(self):
        return self.telemetry_item['03: Time Telemetry']['0072: Mission time'].converted

    def __str__(self):
        time_telemetry = self.telemetry_item['03: Time Telemetry']

        mission_time = time_telemetry['0072: Mission time'].converted
        external_time = time_telemetry['0136: External time'].converted

        return 'Mission: {} External: {} DB: {}'.format(mission_time, external_time, self.db_timestamp)


found_mission_times = set()
duplicates = 0

for telemetry_item in bar(entries):
    time_telemetry = telemetry_item['03: Time Telemetry']

    mission_time = time_telemetry['0072: Mission time'].converted.total_seconds()
    external_time = time_telemetry['0136: External time'].converted.total_seconds()

    if (mission_time, external_time) in found_mission_times:
        duplicates += 1
        continue

    found_mission_times.add((mission_time, external_time))

    match = client.query(search_query_next_match.format(mission_time=mission_time, external_time=external_time))  # type: ResultSet

    mapping = EntryMapping(telemetry_item)

    entry_mapping.append(mapping)

    if len(match) == 0:
        not_found += 1
    elif len(match) == 1:
        found += 1
        dt = dateutil.parser.parse(list(match.items()[0][1])[0]['time'])
        match_mission_time = timedelta(seconds=list(match.items()[0][1])[0]['Time Telemetry.Mission time'])
        delta = match_mission_time - mapping.mission_time()

        mapping.match_to(dt - delta)
    else:
        inconclusive += 1
        print 'Unconclusive match for {} (found {})'.format(mission_time, len(match))

print 'Found matches {}\nNot found {}\nInconclusive {}\nDuplicates {}'.format(found, not_found, inconclusive, duplicates)

entry_mapping.sort(key=lambda f: f.mission_time())

current_timestamp = MISSION_START

previous_entry = None

for item in entry_mapping:
    if item.db_timestamp is not None:
        current_timestamp = item.db_timestamp
    elif previous_entry is not None:
        delta = item.mission_time() - previous_entry.mission_time()
        item.match_to(current_timestamp + delta)
    else:
        delta = item.mission_time()
        item.match_to(MISSION_START + delta)

    current_timestamp = item.db_timestamp
    previous_entry = item

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

url = urlparse(args.influx)
db = InfluxDBClient(host=url.hostname, port=url.port, database=url.path.strip('/'))

db.write_points(all_points)
