import argparse
import sys
from datetime import datetime
from pprint import pprint
from urlparse import urlparse

from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

ZERO_BEACONS_QUERY = """
select time, "Startup.Boot Counter" from beacon where "Startup.Boot Counter" = 0
"""

DELETE_QUERY = """
delete where time = '{}'
"""


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("influx", help="InfluxDB URL (http://<serve>:<port>/<database>")

    return parser.parse_args()


def format_time(t):
    t = t.replace('T', ' ')
    t = t.replace('Z', '')
    dot_idx = t.rfind('.')
    if dot_idx >= 0:
        t = t[:dot_idx]

    return t


def print_times(times):
    print 'Found zero beacons at times (UTC):'

    prev_date = None

    for t in times:
        t = format_time(t)
        date = t.split(' ')[0]
        if date != prev_date:
            print '{}:'.format(date)

        print '\t{}'.format(t)

        prev_date = date


def ask_for_remove():
    print '\nAre dates above correct dates for power cycles?'
    print "\tType 'y<enter>' to remove them"
    print "\tType 'n<enter>' to abort"
    print '\tType anything else if you can not read'

    i = raw_input('[y/n]: ')

    if i == 'y':
        return True
    elif i == 'n':
        return False
    else:
        print "Apparently you can't read, so any error message is meaningless to you"
        sys.exit(42)


def remove_at(db, beacon_time):
    print '\t{}'.format(format_time(beacon_time))
    db.query(DELETE_QUERY.format(beacon_time))


def main(args):
    url = urlparse(args.influx)
    db = InfluxDBClient(host=url.hostname, port=url.port, database=url.path.strip('/'))

    result = db.query(ZERO_BEACONS_QUERY)  # type: ResultSet
    beacons = result.get_points('beacon')

    zero_beacon_times = []

    for beacon in beacons:
        t = beacon['time']  # type: str

        zero_beacon_times.append(t)

    if len(zero_beacon_times) == 0:
        print 'No zero-beacons found!'
        return

    print_times(zero_beacon_times)

    if not ask_for_remove():
        print 'NOT removing data'
        return

    print 'Removing data...'

    for t in zero_beacon_times:
        remove_at(db, t)


main(parse_args())
