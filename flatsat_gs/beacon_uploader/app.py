import argparse
import logging
from pprint import pprint
from urlparse import urlparse

from datetime import datetime, timedelta
from influxdb import InfluxDBClient

import response_frames
from data_point import generate_data_points
from radio.radio_receiver import Receiver
from tools.parse_beacon import ParseBeacon
from utils import ensure_byte_list


class BeaconUploaderApp(object):
    @staticmethod
    def main(args):
        parser = argparse.ArgumentParser()

        parser.add_argument('-t', '--downlink-host', required=False,
                            help="GNURadio host", default='localhost')
        parser.add_argument('-p', '--downlink-port', required=False,
                            help="GNURadio port", default=7001, type=int)

        parser.add_argument('-d', '--influx', required=False,
                            help="InfluxDB url", default='http://localhost:8086/pwsat2')

        BeaconUploaderApp(parser.parse_args(args))._run()

    def __init__(self, args):
        self._args = args
        self._log = logging.getLogger("App")

        self._receiver = Receiver(args.downlink_host, args.downlink_port)
        self._frame_decoder = response_frames.FrameDecoder(response_frames.frame_factories)

        url = urlparse(args.influx)
        self._db = InfluxDBClient(host=url.hostname, port=url.port, database=url.path.strip('/'))

    def _run(self):
        self._log.info("Pushing beacons from tcp://%s:%d to %s", self._args.downlink_host, self._args.downlink_port,
                       self._args.influx)

        # data = self._receiver.decode_kiss(self._receiver.receive())
        # print self._frame_decoder.decode(data)

        with open('C:/PW-Sat/obc-build/build/FlightModel/FlightModel/reports/telemetry', 'rb') as f:
            raw_frame = f.read()
            raw_frame = [0xCD] + ensure_byte_list(raw_frame)
            beacon = self._frame_decoder.decode(raw_frame)

            self._process_single_beacon(datetime.utcnow(), beacon)

    def _process_single_beacon(self, timestamp, beacon):
        telemetry = ParseBeacon.parse(beacon)

        points = generate_data_points(timestamp, telemetry)

        self._db.write_points(points)

    def _build_key(self, group, field):
        group = group[4:]
        field = field[6:]
        return group + "." + field

    def _decode_value(self, o):
        if isinstance(o, timedelta):
            return o.total_seconds()

        try:
            return self._decode_value(o.converted)
        except AttributeError:
            return o
