import argparse
import logging
from urlparse import urlparse

from influxdb import InfluxDBClient

import response_frames
from radio.radio_receiver import Receiver


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
        self._log.info("Pushing beacons from tcp://%s:%d to %s", self._args.downlink_host, self._args.downlink_port, self._args.influx)

        print self._db.get_list_database()

        data = self._receiver.decode_kiss(self._receiver.receive())
        print self._frame_decoder.decode(data)
